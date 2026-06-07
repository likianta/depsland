import sys

import streamlit_canary as sc
from argsense import cli
from lk_utils import run_cmd_args


@cli
def demo():
    run_cmd_args(
        (
            sys.executable,
            'depsland/gui/setup_wizard/depsland_installer_client_support.py',
            'start-server',
        ),
        verbose=True,
        blocking=False,
    )
    run_cmd_args(
        (
            sys.executable,
            'depsland/gui/setup_wizard/depsland_installer_client_support.py',
            'start-client',
            'localhost',
        ),
        verbose=True,
        blocking=False,
    )
    sc.run(
        'depsland/gui/setup_wizard/depsland_installer_online.py',
        port=3001,
        extra_args=(
            '--debug',
            '--client-public-host',
            'localhost',
            '--client-public-port',
            '22187',
            '--target-appid',
            'hello_world_tkinter',
            '--target-version',
            '0.5.0',
        ),
    )


if __name__ == '__main__':
    cli.run()
