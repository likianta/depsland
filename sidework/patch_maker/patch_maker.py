import typing as tp

from argsense import cli
from lk_utils import fs
from lk_utils import run_cmd_args
from lk_utils import uuid
from neoprint import print

from depsland import make_temp_dir
from depsland.manifest import T as T0
from depsland.manifest import diff_manifest
from depsland.manifest import load_manifest


class T:
    AbsPath = T0.AbsPath
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
def make_patch(old_manifest_file: str, new_manifest_file: str) -> None:
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

    _resolve_assets(
        diff['assets'],
        new_manifest['start_directory'],
        '{}/assets'.format(temp_dir),
    )
    # _resolve_dependencies(diff['dependencies'], ...)

    exe = _generate_patch_executable(patch_id)
    print(
        'see generated executable: {} ({})'.format(
            fs.relpath(exe, fs.here()), fs.filesize(exe, str)
        ),
        ':v4',
    )


def _resolve_assets(
    assets_diff: T.AssetsDiff, root_i: str, root_o: str
) -> tp.Tuple[T.AbsPath, T.AbsPath]:
    """
    ref: depsland/api/user_api/install.py:_install_files
    """
    assets_map: T.AssetsMap = {}
    for action, (relpath, real_relpath), (info0, info1) in assets_diff:
        if action == 'append' or action == 'update':
            abspath = '{}/{}'.format(root_i, real_relpath)
            assert fs.exist(abspath)
            assets_map[info1.uid] = (
                abspath,
                relpath,
                info1.type == 'dir',
                True,
            )
        elif action == 'delete':
            assets_map[info0.uid] = (None, relpath, info0.type == 'dir', False)

    for file_id, (abspath, relpath, isdir, _) in assets_map.items():
        if abspath:
            print('add asset to temp dir', relpath, file_id, ':in')
            fs.make_link(abspath, '{}/{}'.format(root_o, file_id), False)

    simplified_assets_map = {
        k: '{}:{}{}'.format(v[1], '1' if isdir else '0', '1' if v[2] else '0')
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
