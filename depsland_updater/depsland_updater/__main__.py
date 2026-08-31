from argsense import cli
from .main import request_patch

cli.add_cmd(request_patch)

if __name__ == '__main__':
    # see also `depsland/api/dev_api/build_offline.py:_create_launcher
    # :patch maker`
    cli.run()
