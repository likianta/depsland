import airmise as air
from lk_utils import fs
from argsense import cli

@cli
def start_server():
    air.frp.run_transceiver(port=2186)

@cli
def start_client(target_host, target_port=2186):
    air.frp.connect_to_public_transport(
        {'test': _greeting_test},
        source_port=2187,
        target_host=target_host,
        target_port=target_port,
    )

def _list_folder_tree():
    ...

def _greeting_test(name):
    print(f'hello {name}')
    return 'Hello {}!'.format(name)

if __name__ == '__main__':
    # debug mode:
    #   terminal 1:
    #       pox depsland/gui/setup_wizard/depsland_installer_client_support.py
    #           start-server
    #   terminal 2:
    #       pox depsland/gui/setup_wizard/depsland_installer_client_support.py
    #           start-client localhost
    #       you will get a "public port".
    #   terminal 3:
    #       strun 2185 depsland/gui/setup_wizard/depsland_installer_online.py
    #           localhost <public_port>
    # production mode:
    #   run this command in aliyun ecs:
    #       python depsland/gui/setup_wizard
    #           /depsland_installer_client_support.py start_server
    cli.run()
