import airmise as air
import os
import pyapp_window
from neoprint import print


def patch_online(open_window: bool = True) -> None:
    possible_server_hosts = (
        # 'localhost',  # mostly used in development
        '172.20.128.100',  # used in local area network
        '47.102.108.149',  # TODO: how to get a free port from public host?
    )

    client = air.ProxyClient()
    for svr_host in possible_server_hosts:
        try:
            client.connect(svr_host, 2192, timeout=3)
            #   see `depsland/gui/patch_maker_online/server.py:mainloop`.
        except Exception:
            continue
        else:
            print(
                'connect to server',
                os.environ['USERNAME'],
                svr_host,
                client.uid,
                ':v4lnt',
            )
            break
    else:
        raise Exception('no server site available')

    if open_window:
        pyapp_window.open_window(
            title='Depsland Updater (Patch Online)',
            url='http://{}:2190/?uid={}'.format(svr_host, client.uid),
            #   see also `depsland/gui/patch_maker_online/server.py
            #   :_register_client` and `depsland/gui/patch_maker_online
            #   /remote_client.py:init_air_client`.
            icon=os.path.normpath('{}/../launcher.ico'.format(__file__)),
            size=(1080, 1210),
            blocking=False,
            verbose=True,
        )

    client.mainloop()  # blocking


if __name__ == '__main__':
    patch_online()
