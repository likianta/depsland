import os
import typing as tp

import airmise as air
import neorpint as np
from lk_utils import fs
from neoprint import print


def patch_online(open_window: bool = False, debug: bool = False) -> None:
    client = air.ProxyClient()
    try:
        client.connect(
            (  # possible server hosts
                # 'localhost',  # mostly used in development
                '172.20.128.100',  # used in local area network
                '47.102.108.149',
            ),
            port=2192,
            timeout=3,
        )
    except Exception:
        print(':v8p', 'no server site available')
        return
    
    if open_window:
        import pyapp_window

        pyapp_window.open_window(
            title='Depsland Updater (Patch Online)',
            url='http://{}:2190/?uid={}'.format(client.host, client.uid),
            #   see also `depsland/gui/patch_maker_online/server.py
            #   :_register_client` and `depsland/gui/patch_maker_online
            #   /remote_client.py:init_air_client`.
            icon=os.path.normpath('{}/../launcher.ico'.format(__file__)),
            size=(1080, 1210),
            blocking=False,
            verbose=True,
        )

    # if debug:
    #     assert _get_manifest_data() is not None
    #     client._user_namespace['get_manifest_data_2'] = _get_manifest_data

    # client.set_passive()
    client.mainloop(verbose=debug)  # blocking
    # client.mainloop(verbose=debug, fragile=debug)  # blocking


def request_downloading_patch():
    try:
        client = air.Client().connect(
            (
                # 'localhost',
                '172.20.128.100',
                '47.102.108.149',
            ),
            port=2191,
        )
    except Exception:
        print(':v8p', 'no server site available')
        return None

    proj_dir = _get_project_dir()
    manifest_file = '{}/patches/initial_manifest.pkl'.format(proj_dir)
    manifest_data = fs.load(manifest_file)
    appid = manifest_data['appid']
    version = manifest_data['version']
    
    if latest_ver := client.call('has_available_patch', appid, version):
        data = client.call('download_patch', appid, version)
        assets_zip = '{}/patches/{}.zip'.format(proj_dir, latest_ver)
        fs.dump(data, assets_zip, 'binary')

        # TODO
        # with np.spinner('Preparing data'):
        #     url = client.call('prepare_patch', appid, version)
        # assets_zip = '{}/patches/{}.zip'.format(proj_dir, latest_ver)
        # fs.download(url, assets_zip, progress=True)
    else:
        print(':v', 'no available patch found')
        return

    assets_dir = assets_zip.remove_suffix('.zip')
    fs.unzip(assets_zip, assets_dir, progress=True)

    ...


def _get_project_dir() -> str:
    if os.getcwd().endswith('source'):
        proj_dir = fs.parent(os.getcwd())
    else:
        proj_dir = fs.normpath(os.getcwd())
    assert fs.exist('{}/patches'.format(proj_dir))
    assert fs.exist('{}/patches/initial_manifest.pkl'.format(proj_dir))
    assert fs.exist('{}/patches/profile.json'.format(proj_dir))
    assert fs.exist('{}/python'.format(proj_dir))
    assert fs.exist('{}/source'.format(proj_dir))
    assert fs.exist('{}/Check Updates.exe'.format(proj_dir))
    return proj_dir


if __name__ == '__main__':
    patch_online()
