import sys

from argsense import cli
from lk_utils import run_cmd_args


@cli.cmd()
def main(port: int = 3002) -> None:
    run_cmd_args(
        sys.executable, '-m', 'streamlit', 'hello',
        '--server.port', port,
        '--global.developmentMode', 'false',
        verbose=True
    )


if __name__ == '__main__':
    cli.run(main)
