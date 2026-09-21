from functools import partial

import airmise as air
from argsense import cli
from lk_utils import chunkwise
from lk_utils import fs
from lk_utils import uuid
from neoprint import print

from .logic import analyze_assets_diff
from .logic import compress_patch_result
from .logic import create_patch_id
from .logic import generate_patch_result
from .logic import get_latest_version
from .logic import get_manifest_file
from .logic import get_project_path
from .logic import init as init_logic
from .logic import load_current_manifest
from .logic import reload_user_manifest
from ... import paths


def launch_server(bore_secret: str = '') -> None:
    init_logic()
    svr = air.Server()
    svr.run(
        {
            'download_patch': _download_patch,
            'get_compressed_asset': _get_compressed_asset,
            'get_latest_version': get_latest_version,
            'get_manifest': _get_manifest,
            'has_available_patch': _has_available_patch,
            'prepare_assets': _prepare_assets,
        },
        port=2191,
        proxy_host='47.102.108.149' if bore_secret else '',
        proxy_secret=bore_secret,
    )


def _download_patch(appid: str, client_app_version: str) -> bytes:
    project_path = get_project_path(appid)

    version_chain = [client_app_version]

    ov = fs.load(paths.chore.overview)
    xlist = ov[appid][client_app_version]
    latest_ver = xlist[-1]
    version_chain.append(latest_ver)

    temp_key = latest_ver
    while True:
        if temp_key in ov[appid]:
            temp_list = ov[appid][temp_key]
            temp_key = temp_list[-1]
            version_chain.append(temp_key)
        else:
            break
    print(appid, ' -> '.join(version_chain), ':v2')

    if len(version_chain) == 2:
        patch_id = uuid(
            '{}:{}:{}'.format(appid, version_chain[0], version_chain[1])
        )[::4]
        final_diff = fs.load(
            '{}/{}-to-{}.json'.format(
                paths.chore.patch_diff, version_chain[0], version_chain[1]
            )
        )
    else:
        patch_id = uuid(
            '{}:{}:{}'.format(appid, version_chain[0], version_chain[-1])
        )[::4]

        total_diff = {}
        for a, b in chunkwise(version_chain, 2):
            if b is None:
                break

            diff_file = '{}/{}-to-{}.json'.format(paths.chore.patch_diff, a, b)
            diff_dict = fs.load(diff_file)

            for k, v in diff_dict.items():
                a, b = v.rsplit(':', 1)
                relpath = a
                is_dir = b[0] == '1'
                is_add = b[1] == '1'
                if k in total_diff:
                    assert total_diff[k][0] == relpath
                    assert total_diff[k][1] == is_dir
                    if total_diff[k][2] == is_add:
                        if is_add:
                            pass
                        else:
                            raise Exception(
                                'unrealizable action: delete a/b then '
                                'delete a/b'
                            )
                    else:
                        total_diff[k] = (relpath, is_dir, is_add)
                else:
                    for k0, (p0, d0, a0) in tuple(total_diff.items()):
                        if fs.is_parent(p0, relpath):
                            if a0 == is_add:
                                if is_add:  # update a/b then update a/b/c
                                    break
                                else:  # delete a/b then delete a/b/c
                                    raise Exception(
                                        'unrealizable action: delete a/b then '
                                        'delete a/b/c'
                                    )
                            else:
                                if is_add:  # delete a/b then update a/b/c
                                    raise Exception(
                                        'unrealizable action: delete a/b then '
                                        'update a/b/c'
                                    )
                                else:  # update a/b then delete a/b/c
                                    total_diff[k] = (relpath, is_dir, is_add)
                                    break
                        elif fs.is_parent(relpath, p0):
                            if a0 == is_add:
                                if is_add:  # update a/b/c then update a/b
                                    total_diff.pop(k0)
                                    total_diff[k] = (relpath, is_dir, is_add)
                                    break
                                else:  # delete a/b/c then delete a/b
                                    total_diff.pop(k0)
                                    total_diff[k] = (relpath, is_dir, is_add)
                                    break
                            else:
                                if is_add:  # delete a/b/c then update a/b
                                    total_diff.pop(k0)
                                    total_diff[k] = (relpath, is_dir, is_add)
                                    break
                                else:  # update a/b/c then delete a/b
                                    total_diff.pop(k0)
                                    total_diff[k] = (relpath, is_dir, is_add)
                                    break
                        else:
                            continue
                    else:
                        total_diff[k] = (relpath, is_dir, is_add)

            final_diff = {
                k: '{}:{}{}'.format(
                    relpath, 1 if is_dir else 0, 1 if is_add else 0
                )
                for k, (relpath, is_dir, is_add) in total_diff.items()
            }

    dir_i = project_path
    dir_o = '{}/{}/assets'.format(paths.chore.grocery, patch_id)
    file_o = '{}/{}/assets.zip'.format(paths.chore.grocery, patch_id)
    if not fs.exist(file_o):
        fs.make_dirs(dir_o)
        for k, v in final_diff.items():
            a, b = v.rsplit(':', 1)
            relpath = a
            # is_dir = b[0] == '1'
            is_add = b[1] == '1'
            if is_add:
                path_i = '{}/{}'.format(dir_i, relpath)
                path_o = '{}/{}'.format(dir_o, relpath)
                fs.make_link(path_i, path_o)
        fs.zip_dir(dir_o, file_o, progress=True)
    return fs.load(file_o, 'binary')


def _get_compressed_asset(local_path: str) -> bytes:
    return fs.load(local_path, 'binary')


def _get_manifest(appid, version):
    return fs.load(get_manifest_file(appid, version), 'binary')


# DELETE
def _has_available_patch(appid: str, client_app_version: str) -> str:
    ov = fs.load(paths.chore.overview)
    if appid in ov:
        if client_app_version in ov[appid]:
            xlist = ov[appid][client_app_version]
            temp_key = xlist[-1]
            while True:
                if temp_key in ov[appid]:
                    xlist = ov[appid][temp_key]
                    temp_key = xlist[-1]
                else:
                    return temp_key
    return ''


def _prepare_assets(
    appid: str, client_manifest_raw_data: bytes, request_version: str = ''
):
    old_manifest = reload_user_manifest(appid, client_manifest_raw_data)
    new_manifest = load_current_manifest(appid)
    if request_version:
        assert new_manifest['version'] == request_version

    patch_id = create_patch_id(
        appid, old_manifest['version'], new_manifest['version']
    )
    assets_map = analyze_assets_diff(old_manifest, new_manifest)
    assets_dir = generate_patch_result(patch_id, assets_map)

    compress_dir = '{}/compressed'.format(assets_dir)
    fs.make_dir(compress_dir)
    compress_patch_result(assets_map, assets_dir, compress_dir)
    return assets_map, compress_dir


# ------------------------------------------------------------------------------


def launch_proxy_server(bore_secret: str = '') -> None:
    svr = air.ProxyServer()
    svr.run(
        {'list_users': partial(_list_users, svr)},
        port=2192,
        proxy_host='47.102.108.149' if bore_secret else '',
        proxy_secret=bore_secret,
    )


def _list_users(server: air.ProxyServer):
    if server.routes:
        for _, info in server.routes.values():
            yield info
    else:
        yield None


# ------------------------------------------------------------------------------


def list_users() -> None:
    for info in sorted(
        air.Client().connect(port=2192).call('list_users'),
        key=lambda x: x['timestamp'],
        reverse=True,
    ):
        if info is None:
            print('no active users')
            break
        print(info, ':iln')


if __name__ == '__main__':
    # python -m depsland.gui.patch_maker_online.server launch_server \
    #   <bore_secret>
    # python -m depsland.gui.patch_maker_online.server launch_proxy_server \
    #   <bore_secret>
    # ---
    # cd sidework/depsland_updater
    # python -m depsland_updater patch_online :f
    # ---
    # python depsland/gui/patch_maker_online/server.py list_users
    #   we can see `unique_id` in the info list. copy it and visit
    #   `http://localhost:2190/?uid=<unique_id>`. see also
    #   `depsland/gui/patch_maker_online/app.py`.

    cli.add_cmd(launch_server)
    cli.add_cmd(launch_proxy_server)
    cli.add_cmd(list_users)
    cli.run()
