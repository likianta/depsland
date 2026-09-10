import streamlit_canary as sc
from argsense import cli
from depsland.gui.patch_maker_online import server


@cli
def launch_server() -> None:
    print(
        'server will start at port 2192, the next step you can bring up '
        '`sidework/depsland_updater/patch_client.py:patch_online`',
        ':v2',
    )
    server.mainloop()  # blocking


@cli
def launch_gui(
    debug: bool = False, local: bool = False, _blocking: bool = True
) -> None:
    extra_args = ['--developer-mode']
    if debug:
        extra_args.append('--debug')
    if local:
        extra_args.append('--local-test')
    sc.run(
        'depsland/gui/patch_maker_online/app.py',
        port=2190,
        extra_args=extra_args,
        show_window=False,
        blocking=_blocking,
    )


@cli
def launch_gui_and_server(**kwargs) -> None:
    launch_gui(**kwargs, _blocking=False)
    launch_server()


if __name__ == '__main__':
    # python run/patch_maker.py launch_server
    # python run/patch_maker.py launch_gui --debug
    # python run/patch_maker.py launch_gui --debug --local
    # python run/patch_maker.py launch_gui_and_server --debug :true
    cli.run()
