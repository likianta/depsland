if __name__ == '__main__':
    __package__ = 'depsland.gui.setup_wizard'

import airmise as air
import streamlit_canary as sc
import sys
import typing as tp
from lk_utils import fs
from lk_utils import run_cmd_args
from lk_utils import run_new_thread
from lk_utils.subproc import Popen
from time import sleep
from ... import paths

state = {
    'frontend_started': False,
    'frontend_timeout': 20,
    'setup_finished': False,
    'run_after_setup': False,
}


def sequential_launch(appid, name, version, dry_run: bool = False):
    run_new_thread(
        air.run_server,
        {'start': _notify_started, 'close': _close_setup_wizard},
        port=2184,
    )

    proc_st, proc_win = tp.cast(
        tp.Tuple[Popen, Popen],
        sc.run(
            title='Depsland Setup Wizard',
            icon=paths.build.launcher_icon,
            target=fs.xpath('./setup_wizard.py'),
            extra_args=(
                name,
                appid,
                ':empty',  # TODO: description
                '--dry-run' if dry_run else '--not-dry-run',
                '--emit-close-event',
            ),
            port=2183,
            show_window=True,
            # size=(1340, 960),
            size=(870, 590),
            subthread=True,
        ),
    )

    while True:
        # print('polling...', ':vi')
        if state['setup_finished']:
            proc_win.kill()
            proc_st.kill()
            break
        elif not proc_win.is_alive:
            if state['frontend_started']:
                print('user closed setup window')
                assert not state['run_after_setup']
                proc_st.kill()
                break
            else:
                state['frontend_timeout'] -= 1
                if state['frontend_timeout'] <= 0:
                    raise TimeoutError('timeout waiting for opening app window')
        sleep(1)

    air.default_client.close()

    if state['run_after_setup']:
        if dry_run:
            print('run target application...', appid, name, version)
        else:
            run_cmd_args(
                (sys.executable, '-m', 'depsland', 'run', appid, version),
                blocking=True,
                verbose=True,
                ignore_return=True,
            )
    else:
        if dry_run:
            print('finish without running target application')


def _notify_started() -> None:
    state['frontend_started'] = True
    print('frontend get started')


def _close_setup_wizard(run_after_setup: bool) -> None:
    state['setup_finished'] = True
    state['run_after_setup'] = run_after_setup
    print(state, ':v2')


if __name__ == '__main__':
    # pox depsland/gui/setup_wizard/process_manager.py -h
    # pox depsland/gui/setup_wizard/process_manager.py hello_world
    #   'Hello World Example' 0.0.0 :true
    from argsense import cli

    cli.add_cmd(sequential_launch)
    cli.run(sequential_launch)
