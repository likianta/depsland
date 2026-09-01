from argsense import cli
from .patch_client import patch_online

cli.add_cmd(patch_online)

if __name__ == '__main__':
    # see also `depsland/api/dev_api/build_offline.py:_create_launcher
    # :patch maker`
    cli.run()
