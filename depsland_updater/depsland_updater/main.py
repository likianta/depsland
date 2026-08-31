import airmise as air
import os
from neoprint import print


def check_updates(manifest_file: str):
    pass


def request_patch(port: int = 2193) -> None:
    try_sites = (
        # 'localhost',  # mostly used in development
        air.get_local_ip_address(),  # used in local network
        # '47.102.108.149'  # TODO: how to get a free port from public host?
    )
    client = air.Client()
    for site in try_sites:
        try:
            client.connect(site, 2190, timeout=3)
        except Exception:
            continue
        else:
            print('connected to server', client.url, ':v4')
            break
    else:
        raise Exception('no server site available')
    client.call(
        'register_client',
        air.get_local_ip_address(),
        port,
        os.environ['USERNAME'],
    )
    client.set_passive()


def apply_patch():
    pass
