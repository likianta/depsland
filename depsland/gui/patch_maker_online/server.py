import airmise as air
# from argsense import cli


def mainloop():
    air.Server().run(port=2191)
    air.ProxyServer().run(port=2192)


if __name__ == '__main__':
    # launch server:
    #   python depsland/gui/patch_maker_online/server.py
    # or by depsland:
    #   python -m depsland patch_maker_server
    # expose service to public (optional):
    #   bore local -s <secret> -t 47.102.108.149 -p 2192 2192
    mainloop()
