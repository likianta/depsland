import typing as t
from threading import Thread
from time import sleep

import psutil
import streamlit as st
from lk_utils import fs
from streamlit.runtime.scriptrunner import RerunData
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner import add_script_run_ctx
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit_extras.row import row as st_row

from ..api.user_api import run_app
from ..paths import apps as app_paths


def get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            # 'installed_apps': {},
            'processes': {},  # {appid: pid, ...}
        }
        
        thread = Thread(
            target=_poll_processes_states,
            args=(st.session_state[__name__]['processes'],),
            daemon=True
        )
        # FIXME: `add_script_run_ctx` resolves error of accessing -
        #   `st.session_state` in subthread. but cannot reflect `st.rerun` -
        #   request to the main thread.
        #   https://discuss.streamlit.io/t/changing-session-state-not-
        #   reflecting-in-active-python-thread/37683/2
        #   it seems that there is NO WAY could change main thread's ui states -
        #   from subthread...
        add_script_run_ctx(thread)
        thread.start()
    
    return st.session_state[__name__]


def main() -> None:
    session = get_session()
    cols = st.columns(2)
    colx = -1  # column index
    for app_name, vers in list_installed_apps():
        colx += 1
        with cols[colx % 2]:
            with st.container(border=True):
                is_running = app_name in session['processes']
                st.write(':blue[**{}**] {}'.format(
                    app_name, '(running)' if is_running else ''
                ))
                target_ver = st.selectbox(
                    'Version ({})'.format(len(vers)),
                    vers,
                    key=f'{app_name}:version',
                )
                
                button_row = st_row((9, 2))
                with button_row.container():
                    if is_running:
                        if st.button(
                            ':red[Stop]',
                            key=f'{app_name}:stop',
                            use_container_width=True,
                        ):
                            pid = session['processes'].pop(app_name)
                            _kill_process_tree(pid)
                            st.rerun()
                    else:
                        if st.button(
                            ':green[Run]',
                            key=f'{app_name}:run',
                            use_container_width=True,
                        ):
                            popen_obj = run_app(app_name, _version=target_ver)
                            session['processes'][app_name] = popen_obj.pid
                            st.rerun()
                if button_row.button(
                    '⚙️',  # icon from https://getemoji.com/
                    key=f'{app_name}:setting'
                ):
                    with st.container(border=True):
                        st.button(
                            'Add to desktop',
                            key=f'{app_name}:add_to_desktop',
                            use_container_width=True,
                        )


def list_installed_apps() -> t.Iterator[t.Tuple[str, t.List[str]]]:
    for d in fs.find_dirs(app_paths.root):
        if d.name.startswith('.'):
            continue
        if fs.exists(x := f'{d.path}/.inst_history'):
            history = fs.load(x).splitlines()
            yield d.name, history


def _poll_processes_states(processes: dict) -> None:
    print('start polling', ':dv')
    # session = get_session()
    temp = 0
    while True:
        temp += 1
        if processes:
            dirty = False
            for app_name, pid in tuple(processes.items()):
                print(app_name, pid, psutil.pid_exists(pid), ':v')
                if not psutil.pid_exists(pid):
                    processes.pop(app_name)
                    dirty = True
            if dirty:
                # st.rerun()
                # raise Exception('rerun required')
                ctx = get_script_run_ctx()
                # ctx.script_requests.request_rerun(
                #     RerunData(
                #         query_string=ctx.query_string,
                #         page_script_hash=ctx.page_script_hash,
                #     )
                # )
                raise RerunException(
                    RerunData(
                        query_string=ctx.query_string,
                        page_script_hash=ctx.page_script_hash,
                    )
                )
        print(f'am i alive ({temp})?', ':v')
        sleep(1)


def _kill_process_tree(pid: int) -> None:
    """
    https://stackoverflow.com/questions/70565429/how-to-kill-process-with-
    entire-process-tree-with-python-on-windows
    """
    proc = psutil.Process(pid)
    print('kill [{}] {}'.format(pid, proc.name()), ':iv4s')
    for child in proc.children(recursive=True):
        print('    |- kill [{}] {}'.format(child.pid, child.name()), ':iv4s')
        child.kill()
    proc.kill()
    print(':i0s')
