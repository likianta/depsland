import airmise as air
from argsense import cli

@cli
def start_server() -> None:
    air.frp.run_transceiver(port=2186)

@cli
def start_client(target_host: str, target_port: int = 2186) -> None:
    air.frp.connect_to_public_transport(
        {'test': _greeting_test},
        source_port=2187,
        target_host=target_host,
        target_port=target_port,
    )

def _greeting_test(name: str) -> str:
    print(f'hello {name}')
    return 'Hello {}!'.format(name)

if __name__ == '__main__':
    # command: see `./readme.mo : Demo Run`
    cli.run()
