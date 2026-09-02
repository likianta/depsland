import airmise as air

from argsense import cli
from functools import partial
from neoprint import print


def mainloop():
    # air.Server().run(port=2191)
    svr = air.ProxyServer()
    svr.run({'list_users': partial(_list_users, svr)}, port=2192)


def _list_users(server: air.ProxyServer):
    if server.routes:
        for (_, info) in server.routes.values():
            yield info
    else:
        yield None


# ------------------------------------------------------------------------------


def list_users() -> None:
    for info in sorted(
        air.Client().connect(port=2192).call('list_users'),
        key=lambda x: x['timestamp'],
        reverse=True,
    ):
        if info is None:
            print('no active users')
            break
        print(info, ':iln')


if __name__ == '__main__':
    # launch server:
    #   python depsland/gui/patch_maker_online/server.py mainloop
    # or by depsland:
    #   python -m depsland patch_maker_server
    # expose service to public (optional):
    #   bore local -s <secret> -t 47.102.108.149 -p 2192 2192
    # ---
    # cd sidework/depsland_updater
    # python -m depsland_updater patch_online :f
    # ---
    # python depsland/gui/patch_maker_online/server.py list_users
    #   we can see `unique_id` in the info list. copy it and visit 
    #   `http://localhost:2190/?uid=<unique_id>`. see also 
    #   `depsland/gui/patch_maker_online/app.py`.

    # mainloop()
    cli.add_cmd(mainloop)
    cli.add_cmd(list_users)
    cli.run()
