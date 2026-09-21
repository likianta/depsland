import typing as tp

from lk_utils import fs
from lk_utils import run_cmd_args
from lk_utils import uuid
from neoprint import format
from neoprint import print

from ... import paths
from ...manifest import T as T0
from ...manifest import diff_manifest
from ...manifest import load_manifest


class T:
    AssetsMap = tp.Dict[
        str, tp.Tuple[tp.Optional[T0.AbsPath], T0.RelPath, bool, int, T0.Action]
        # ^ file_id   ^ src_abspath, dst_relpath, isdir, size, action
        #   notice: AssetsMap is order sensitive: the "delete" action must be
        #   first. because if we have both `append:A` and `delete:A/B`, latter
        #   delete will make loss to append action.
    ]
    Manifest = T0.ManifestObject


_appid_to_project_path = {}


def init() -> None:
    _appid_to_project_path.update(
        fs.load(paths.chore.appid_to_project, default=dict)
    )
    assert _appid_to_project_path


# ------------------------------------------------------------------------------


def analyze_assets_diff(
    old_manifest: T.Manifest, new_manifest: T.Manifest
) -> T.AssetsMap:
    root = new_manifest['start_directory']
    diff = diff_manifest(old=old_manifest, new=new_manifest)

    assets_map: T.AssetsMap = {}
    for action, (relpath, real_relpath), (info0, info1) in diff['assets']:
        if action == 'ignore':
            continue
        print(action, relpath, ':inv')
        if action == 'append' or action == 'update':
            abspath = '{}/{}'.format(root, real_relpath)
            assert fs.exist(abspath), format(root, relpath, real_relpath, ':nl')
            size = tp.cast(
                int, fs.filesize(abspath, recursive=info1.type == 'dir')
            )
            assets_map[info1.uid] = (
                abspath,
                relpath,
                info1.type == 'dir',
                size,
                action,
            )
        else:  # 'delete'
            assets_map[info0.uid] = (
                None,
                relpath,
                info0.type == 'dir',
                -1,
                action,
            )
    print(len(assets_map), ':n')
    return dict(
        sorted(
            assets_map.items(),
            key=lambda kv: (0 if kv[1][4] == 'delete' else 1, kv[0]),
            #   put delete actions first. see reason in `T.AssetsMap:comment`.
        )
    )


def compress_patch_result(
    assets_map: T.AssetsMap, assets_dir: str, compress_dir: str = ''
) -> None:
    """
    Note: This may be time consuming.
    """
    if not compress_dir:
        compress_dir = assets_dir
    for uid, (abspath, relpath, is_dir, size, action) in assets_map.items():
        if action == 'delete':
            continue
        if is_dir:
            path_i = '{}/{}'.format(assets_dir, uid)
            path_o = '{}/{}.zip'.format(compress_dir, uid)
            fs.zip(path_i, path_o)
        else:
            path_i = '{}/{}'.format(assets_dir, uid)
            path_o = '{}/{}.nozip'.format(compress_dir, uid)
            fs.make_link(path_i, path_o)


def create_patch_id(appid: str, old_ver: str, new_ver: str) -> str:
    # 8-character hex string. e.g. 'd514b17f'
    patch_id = uuid('{}:{}:{}'.format(appid, old_ver, new_ver))[::4]
    print(appid, old_ver, new_ver, patch_id, ':pv2nl')
    return patch_id


def generate_patch_executable(
    patch_id: str, assets_map: T.AssetsMap, assets_dir: str
) -> str:
    simplified_assets_map = {}
    for k, (abspath, relpath, is_dir, size, action) in assets_map.items():
        simplified_assets_map[k] = '{}:{}{}'.format(
            relpath,
            '1' if is_dir else '0',
            '0' if size == -1 else '1',
            # format: `<relpath>:<is_dir><action>`
            #   action: 1 for append/update, 0 for delete.
        )

    # `chore/patch_maker/patch_extractor_template.v` requires the following
    # three files.
    fs.dump(simplified_assets_map, paths.chore.assets_map)
    fs.zip(assets_dir, paths.chore.assets_zip, True, progress=True)
    # TODO: dump_manifest(state.new_manifest, paths.chore.manifest_pkl)

    # requires vlang to be installed globally.
    run_cmd_args(
        (
            'v',
            '-o',
            'generated_patches/patch-{}.exe'.format(patch_id),
            'patch_extractor_template.v',
        ),
        cwd=paths.chore.patch_maker,
        verbose=True,
    )
    return '{}/patch-{}.exe'.format(paths.chore.generated_patches, patch_id)


def generate_patch_result(
    patch_id: str, assets_map: T.AssetsMap, reuse: bool = True
) -> str:
    """
    Dump assets map to a temp directory. The remote can download resources by
    urls in multi-thread.
    """
    assets_dir = '{}/{}/assets'.format(paths.chore.grocery, patch_id)
    if fs.exist(assets_dir):
        if reuse:
            return assets_dir
        fs.remove_tree(assets_dir)
    fs.make_dirs(assets_dir)
    for uid, (abspath, relpath, is_dir, size, action) in assets_map.items():
        if abspath:
            print('add resource', '{} ({})'.format(relpath, uid), ':iv2')
            fs.make_link(abspath, '{}/{}'.format(assets_dir, uid), False)
    return assets_dir


def get_manifest_file(appid: str, version: str = '') -> str:
    if not version:
        version = get_latest_version(appid)
    file = '{}/{}/{}/manifest.pkl'.format(paths.apps.root, appid, version)
    assert fs.exist(file), file
    return file


def get_project_path(appid: str) -> str:
    return _appid_to_project_path[appid]


def get_latest_version(appid: str) -> str:
    local_app_dir = '{}/{}'.format(paths.apps.root, appid)
    history_file = '{}/history.txt'.format(local_app_dir)
    return fs.load(history_file).split('\n', 1)[0]


def load_current_manifest(appid: str) -> T.Manifest:
    # proj_path = _appid_to_project_path[appid]
    # mani_file = '{}/.depsland/manifest.pkl'.format(proj_path)

    mani_file = get_manifest_file(appid)
    mani_data = load_manifest(
        mani_file, start_directory=_appid_to_project_path[appid]
    )
    return mani_data


def reload_user_manifest(appid: str, raw_data: bytes) -> T.Manifest:
    fs.dump(raw_data, paths.chore.user_manifest, 'binary')
    return load_manifest(
        paths.chore.user_manifest, start_directory=_appid_to_project_path[appid]
    )
