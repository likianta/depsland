from argsense import cli
from .direct_request import request_patch
from .proxy_service import patch_online

cli.add_cmd(patch_online)
cli.add_cmd(request_patch)

if __name__ == '__main__':
    # python -m depsland_updater -h
    # python -m depsland_updater patch_online
    # python -m depsland_updater request_patch --debug
    # see also `depsland/api/dev_api/build_offline.py:_create_launcher
    # :patch maker`
    cli.run()
