import os
import typing as tp

import airmise as air
from lk_utils import fs
from neoprint import print


class T:
    OverView = tp.TypedDict(
        'OverView',
        {
            'appid': str,
            'initial_version': str,
            'current_version': str,
            'downloaded_version': str,
            # 'patched_version': str,
        },
    )


def request_patch(debug: bool = False) -> None:
    try:
        client = air.Client().connect(
            ('localhost', '172.20.128.100', '47.102.108.149'), port=2191
        )
    except Exception:
        client = None
        # print(':v8p', 'no server site available')
        # return

    if debug:
        proj_dir = 'C:/Likianta/apps/depsland/jlpdf_watermaker_0xf964-2.0.0a8'
    else:
        proj_dir = get_project_dir()
    ov: T.OverView = fs.load('{}/patches/overview.json'.format(proj_dir))
    print(ov, ':lnv2')

    if client:
        latest_ver = client.call('get_latest_version', ov['appid'])
        print(latest_ver, ':nt1')
        if latest_ver and ov['current_version'] != latest_ver:
            if ov['downloaded_version']:
                if ov['downloaded_version'] == latest_ver:
                    apply_patch_from_local(
                        proj_dir=proj_dir, version=ov['downloaded_version']
                    )
                    ov['current_version'] = latest_ver
                    ov['downloaded_version'] = ''
                    fs.dump(ov, '{}/patches/overview.json'.format(proj_dir))
                    return
                else:
                    assert ov['downloaded_version'] < latest_ver  # TODO

            patch_dir = init_patch_dir(proj_dir, latest_ver)
            download_latest_manifest(client, ov['appid'], latest_ver, patch_dir)
            assets_map = download_patch_from_server(
                client, ov['appid'], ov['current_version'], latest_ver, proj_dir
            )
            ov['downloaded_version'] = latest_ver

            apply_patch_from_local(
                proj_dir=proj_dir, version=latest_ver, assets_map=assets_map
            )
            ov['current_version'] = latest_ver
            ov['downloaded_version'] = ''

            fs.dump(ov, '{}/patches/overview.json'.format(proj_dir))
        else:
            print(
                'You are up to date (v{})'.format(ov['current_version']), ':v4'
            )
    else:
        if ov['downloaded_version']:
            raise NotImplementedError
        else:
            print(':v8p', 'no server site available')


def apply_patch_from_local(
    version: str,
    proj_dir: tp.Optional[str] = None,
    assets_map: tp.Optional[dict] = None,
) -> None:
    if not proj_dir:
        proj_dir = get_project_dir()
    if not assets_map:
        assets_map = fs.load(
            '{}/patches/{}/assets_map.pkl'.format(proj_dir, version)
        )

    assets_dir = '{}/patches/{}/assets'.format(proj_dir, version)
    delete_dir = '{}/patches/{}/backups'.format(proj_dir, version)

    print(':d', 'apply patch v{}'.format(version))
    for uid, (_, relpath, is_dir, size, action) in assets_map.items():
        print(
            '[{}]{}[/] {} [dim]({})[/]'.format(
                'red' if action == 'delete' else 'green', action, relpath, uid
            ),
            ':ir',
        )
        if action == 'delete':
            path_i = '{}/source/{}'.format(proj_dir, relpath)
            path_o = '{}/{}'.format(delete_dir, uid)
            if fs.exist(path_i):
                fs.move(path_i, path_o, True)
            else:
                print(
                    ':v6n',
                    '`path_i` is about to delete, but it is already gone',
                    path_i,
                )
        else:
            path_i = '{}/{}'.format(assets_dir, uid)
            path_o = '{}/source/{}'.format(proj_dir, relpath)
            if fs.exist(path_o):
                fs.move(path_o, '{}/{}'.format(delete_dir, uid), True)
            fs.make_link(path_i, path_o, False)
    print('patch applied', ':v4')


def download_latest_manifest(
    client: air.Client, appid: str, version: str, patch_dir: str
) -> None:
    data_bytes = client.call('get_manifest', appid, version)
    fs.dump(data_bytes, '{}/manifest.pkl'.format(patch_dir), 'binary')


def download_patch_from_server(
    client: air.Client, appid: str, old_ver: str, new_ver: str, proj_dir
) -> dict:
    print('ask server to prepare assets, this may take a while...')
    old_patch_dir = '{}/patches/{}'.format(proj_dir, old_ver)
    new_patch_dir = '{}/patches/{}'.format(proj_dir, new_ver)

    old_mani_data_bytes = fs.load(
        '{}/manifest.pkl'.format(old_patch_dir), 'binary'
    )
    assets_map, remote_assets_dir = client.call(
        'prepare_assets', appid, old_mani_data_bytes, old_ver, new_ver
    )
    fs.dump(assets_map, f'{new_patch_dir}/assets_map.pkl')

    print('download assets from server', ':d')
    patch_dir = new_patch_dir
    for uid, (_, relpath, is_dir, size, action) in assets_map.items():
        if action == 'delete':
            continue
        print('{} [dim]({})[/]'.format(relpath, uid), ':irv2')
        ext = 'zip' if is_dir else 'nozip'
        data_i = client.call(
            'get_compressed_asset',
            '{}/{}.{}'.format(remote_assets_dir, uid, ext),
        )
        file_m = '{}/assets/{}.{}'.format(patch_dir, uid, ext)
        path_o = '{}/assets/{}'.format(patch_dir, uid)
        fs.dump(data_i, file_m, 'binary')
        if is_dir:
            fs.unzip(file_m, path_o, True)
            fs.remove_file(file_m)
        else:
            fs.move(file_m, path_o, True)
    print('done, see "{}"'.format(patch_dir))
    return assets_map


def get_project_dir() -> str:
    if os.getcwd().endswith('source'):
        proj_dir = fs.parent(os.getcwd())
    else:
        proj_dir = fs.normpath(os.getcwd())
    assert fs.exist('{}/patches'.format(proj_dir))
    assert fs.exist('{}/patches/initial_manifest.pkl'.format(proj_dir))
    assert fs.exist('{}/patches/overview.json'.format(proj_dir))
    assert fs.exist('{}/python'.format(proj_dir))
    assert fs.exist('{}/source'.format(proj_dir))
    assert fs.exist('{}/Check Updates.exe'.format(proj_dir))
    return proj_dir


def init_patch_dir(proj_dir: str, version: str) -> str:
    patch_dir = '{}/patches/{}'.format(proj_dir, version)
    if not fs.exist(patch_dir):
        fs.make_dir(f'{patch_dir}')
        fs.make_dir(f'{patch_dir}/assets')
        fs.make_dir(f'{patch_dir}/backups')
    return patch_dir


if __name__ == '__main__':
    request_patch()
