import airmise as air

# from argsense import cli
from functools import partial
from neoprint import print


def mainloop():
    # air.Server().run(port=2191)
    svr = air.ProxyServer()
    svr.run(
        {
            # 'list_connections': _list_connections,
            # 'refresh_user_info': _refresh_user_info,
            'list_users': partial(_list_users, svr)
        },
        port=2192,
    )


def _list_users(server: air.ProxyServer):
    if server.routes:
        for uid, (_, info) in server.routes.items():
            yield {
                'user_name': info['user_name'],
                'ip': info['ip'],
                'port': info['connection_port'],
                'uid': uid,
                'register_time': info['register_time'],
            }
    else:
        yield None


# ------------------------------------------------------------------------------


def list_users() -> None:
    for info in sorted(
        air.Client().connect(port=2192).call('list_users'),
        key=lambda x: x['register_time'],
        reverse=True,
    ):
        if info is None:
            print('no active users')
            break
        print(info, ':iln')


# ------------------------------------------------------------------------------
# DELETE

_connected_users = {}


def _list_connections():
    # for port, conn in server.connections.items():
    #     if isinstance(conn, air.proxy.Broker):
    #         # print(port, conn.uid, ':in')
    #         yield port, conn.uid
    for k, v in _connected_users.items():
        yield v | {'uuid': k}


def _refresh_user_info(server: air.ProxyServer, uid, user_name, user_ip):
    _connected_users[uid] = {
        'user': user_name,
        'host': user_ip,
        'port': server.routes[uid].port,
    }


if __name__ == '__main__':
    # launch server:
    #   python depsland/gui/patch_maker_online/server.py
    # or by depsland:
    #   python -m depsland patch_maker_server
    # expose service to public (optional):
    #   bore local -s <secret> -t 47.102.108.149 -p 2192 2192
    # ---
    # python depsland/gui/patch_maker_online/server.py list_users
    mainloop()
