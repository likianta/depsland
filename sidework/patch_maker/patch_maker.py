import typing as tp

from argsense import cli
from lk_utils import fs
from lk_utils import run_cmd_args
from lk_utils import uuid
from neoprint import format
from neoprint import print

from depsland import make_temp_dir
from depsland.manifest import T as T0
from depsland.manifest import diff_manifest
from depsland.manifest import dump_manifest
from depsland.manifest import load_manifest


class T:
    AbsPath = T0.AbsPath
    Action = T0.Action
    FileId = str
    RelPath = T0.RelPath
    AssetsDiff = T0.AssetsDiff
    AssetsMap = tp.Dict[
        FileId, tp.Tuple[tp.Optional[AbsPath], RelPath, bool, bool]
    ]
    #   {
    #       fileid: (
    #           src_abspath, dst_relpath, bool isdir, bool append_or_delete
    #       ), ...
    #   }


@cli
def make_patch(
    old_manifest_file: str, new_manifest_file: str, extra_assets: str = ''
) -> None:
    """
    params:
        extra_assets (-e):
            pass a path or a semi-colon-separated list of paths.
            if given path, the format is `@<your_path>`, usually a ".yaml" or -
            ".json" file. the data structure should be:
                include:
                  - <some_relpath>
                  - ...
                exclude:
                  - <some_relpath>
                  - ...
            the `include` and `exclude` are optional. make sure at least one -
            exists.
            if given semi-colon-separated list, the format is
            `<relpath1>;<relpath2>;...`. for example:
                '.depsland/mini_deps/pyarrow;.depsland/mini_deps/pyarrow.libs'
            the string will be split by semi-colon, it will only be treated as
            include.
    """
    old_manifest = load_manifest(old_manifest_file)
    new_manifest = load_manifest(new_manifest_file)

    patch_id = uuid()[::4]  # 8-character hex string. e.g. 'd514b17f'
    print(patch_id, ':n')
    temp_dir = make_temp_dir(patch_id)
    fs.make_dir('{}/assets'.format(temp_dir))
    fs.make_dir('{}/dependencies'.format(temp_dir))

    # ref: depsland/api/dev_api/build_offline_2.py:_copy_assets
    # ref: depsland/api/user_api/install.py:_install_files
    diff = diff_manifest(old=old_manifest, new=new_manifest)

    if extra_assets:
        if extra_assets[0] == '@':
            x = fs.load(extra_assets[1:])
            extra_include = frozenset(x.get('include', ()))
            extra_exclude = frozenset(x.get('exclude', ()))
        else:
            extra_include = None
            extra_exclude = frozenset(extra_assets.split(';'))
        # print(extra_include, extra_exclude, ':nlv')
        # return
    else:
        extra_include = None
        extra_exclude = None

    _resolve_assets(
        diff['assets'],
        fs.parent(new_manifest['start_directory']),  # FIXME
        '{}/assets'.format(temp_dir),
        _include=extra_include,
        _exclude=extra_exclude,
    )
    # _resolve_dependencies(diff['dependencies'], ...)

    dump_manifest(new_manifest, fs.here('grocery/manifest.pkl'))
    #   note: `new_manifest_file` may be json or yaml, but we want pkl format.
    #   so we use `dump_manifest` instead of `fs.copy_file`.
    exe = _generate_patch_executable(patch_id)
    print(
        'see generated executable: {} ({})'.format(
            fs.relpath(exe, fs.here()), fs.filesize(exe, str)
        ),
        ':v4',
    )


def _resolve_assets(
    assets_diff: T.AssetsDiff,
    root_i: str,
    root_o: str,
    _include: tp.Optional[tp.FrozenSet[T.RelPath]] = None,
    _exclude: tp.Optional[tp.FrozenSet[T.RelPath]] = None,
) -> tp.Tuple[T.AbsPath, T.AbsPath]:
    """
    ref: depsland/api/user_api/install.py:_install_files
    """
    assets_map: T.AssetsMap = {}

    def transform_action(action: T.Action) -> T.Action:
        if action == 'append' or action == 'update':
            if _exclude and relpath in _exclude:
                print('exclude', relpath, ':v7p')
                return 'ignore'
            return action
        elif action == 'delete':
            if _include and relpath in _include:
                print('include', relpath, ':v3p')
                return 'ignore'
            return 'delete'
        else:  # 'ignore'
            if _include and relpath in _include:
                print('include', relpath, ':v3p')
                return 'update'
            return 'ignore'

    for action0, (relpath, real_relpath), (info0, info1) in assets_diff:
        action1 = transform_action(action0)
        print(
            action1
            if action1 == action0
            else '{} -> {}'.format(action0, action1),
            relpath,
            ':inv',
        )
        if action1 == 'append' or action1 == 'update':
            abspath = '{}/{}'.format(root_i, real_relpath)
            assert fs.exist(abspath), format(
                root_i, relpath, real_relpath, ':nl'
            )
            assets_map[info1.uid] = (
                abspath,
                relpath,
                info1.type == 'dir',
                True,
            )
        elif action1 == 'delete':
            assets_map[info0.uid] = (None, relpath, info0.type == 'dir', False)

    for file_id, (abspath, relpath, isdir, _) in assets_map.items():
        if abspath:
            print('add', '{} ({})'.format(relpath, file_id), ':iv2')
            fs.make_link(abspath, '{}/{}'.format(root_o, file_id), False)

    simplified_assets_map = {
        k: '{}:{}{}'.format(v[1], '1' if v[2] else '0', '1' if v[3] else '0')
        for k, v in assets_map.items()
    }
    file_map = fs.here('grocery/assets_map.json')
    file_zip = fs.here('grocery/assets.zip')
    fs.dump(simplified_assets_map, file_map)
    fs.zip(root_o, file_zip, True, progress=True)
    return file_map, file_zip


# TODO
# def _resolve_dependencies(deps_diff: T.DependenciesDiff):
#     """
#     ref: depsland/api/user_api/install.py:_install_packages
#     """
#     deps_map = {}  # see also `_resolve_assets:assets_map`
#     for action, pkg_name, (info0, info1) in deps_diff:
#         if action == 'append' or action == 'update':
#             ...
#         elif action == 'delete':
#             ...


def _generate_patch_executable(patch_id: str) -> str:
    run_cmd_args(
        (
            'v',
            '-o',
            'generated_extractors/patch-{}.exe'.format(patch_id),
            'patch_extractor_template.v',
        ),
        cwd=fs.here(),
        verbose=True,
    )
    return fs.here(
        'generated_extractors/{}'.format('patch-{}.exe'.format(patch_id))
    )


if __name__ == '__main__':
    # uvx sidework/patch_maker/patch_maker.py -h
    cli.run(make_patch)
