import sys
from argsense import cli
from lk_utils import run_cmd_args

@cli
def build_depsland_standalone():
    print('see $[build/build_depsland/main.py].')

@cli
def start_depsland_online_service(bore_secret: str, debug: bool = False):
    from .depsland_online import run_all
    run_all(bore_secret, debug=debug)

if __name__ == '__main__':
    cli.run()
