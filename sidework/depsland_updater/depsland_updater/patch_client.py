import airmise as air
import os
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
        print(':v8', 'no server site available')
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

    client.set_passive()
    client.mainloop(verbose=debug)  # blocking
    # client.mainloop(verbose=debug, fragile=debug)  # blocking


if __name__ == '__main__':
    patch_online()
