import streamlit_canary as sc
from argsense import cli
from depsland.gui.patch_maker_online import server


@cli
def launch_server():
    print(
        'server will start at port 2192, the next step you can bring up '
        '`sidework/depsland_updater/patch_client.py:patch_online`',
        ':v2',
    )
    server.mainloop()  # blocking


@cli
def launch_gui(debug: bool = False, _blocking: bool = True):
    sc.run(
        'depsland/gui/patch_maker_online/app.py',
        port=2190,
        extra_args=('--developer-mode',) + (debug and ('--debug',) or ()),
        show_window=False,
        blocking=_blocking,
    )


@cli
def launch_gui_and_server(debug: bool = False):
    launch_gui(debug, _blocking=False)
    launch_server()


if __name__ == '__main__':
    # python run/patch_maker.py launch_server
    cli.run()
