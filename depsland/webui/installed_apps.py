import typing as t
from time import sleep

import psutil
import streamlit as st
from lk_utils import fs
from streamlit_extras.row import row as st_row

from ..api.user_api import run_app
from ..paths import apps as app_paths


def _get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            # 'installed_apps': {},
            'processes': {},  # {appid: pid, ...}
        }
        
        # thread = Thread(
        #     target=_poll_app_states,
        #     args=(st.session_state[__name__]['processes'],),
        #     daemon=True
        # )
        # # `add_script_run_ctx` resolves error of accessing `st.session_state` -
        # # in subthread.
        # # add_script_run_ctx(thread)
        # thread.start()
    
    return st.session_state[__name__]


def main(_reusable_placeholder: st.empty = None) -> None:
    if _reusable_placeholder:
        with _reusable_placeholder:
            temp_container = st.container()
    else:
        cols = st.columns(2)
        with cols[0]:
            temp_container = st.container()
        with cols[1]:
            st.empty()
    
    def check_if_running(app_name: str) -> bool:
        if app_name in session['processes']:
            pid = session['processes'][app_name]
            if psutil.pid_exists(pid):
                return True
            else:
                session['processes'].pop(app_name)
        return False
    
    cols = st.columns(2)
    session = _get_session()
    colx = -1  # column index
    for app_name, vers in list_installed_apps():
        colx += 1
        with cols[colx % 2]:
            with st.container(border=True):
                is_running = check_if_running(app_name)
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
                            popen_obj = run_app(
                                app_name, _version=target_ver, _blocking=False
                            )
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
    if colx >= 0:
        with temp_container:
            if st.button(
                'Refresh app list',
                use_container_width=True,
                help='''
                    Refresh app list. If you find some apps are closed by
                    external operations, but the in-app button state still
                    shows "stop", this function may also help.
                '''
            ):
                st.rerun()


def list_installed_apps() -> t.Iterator[t.Tuple[str, t.List[str]]]:
    for d in fs.find_dirs(app_paths.root):
        if d.name.startswith('.'):
            continue
        if fs.exists(x := f'{d.path}/.inst_history'):
            history = fs.load(x).splitlines()
            yield d.name, history


def _poll_app_states(processes: dict) -> None:
    """
    FIXME or DELETE: 
        this function is not recommended to use. since it cannot reflect -
        `st.rerun` request to the main thread. it means that the frontend ui - 
        won't refresh although the thread has called `st.rerun`.
        related issues:
            https://discuss.streamlit.io/t/changing-session-state-not-
            reflecting-in-active-python-thread/37683/2
            https://discuss.streamlit.io/t/callback-hook-on-a-state-change/29529
        it seems that there is NO WAY could change main thread's ui states -
        from subthread...
    we made an alternative that shows a button for user to manually refresh -
    app states, see `main : st.button('Refresh app list')`.
    """
    print('start polling', ':dv')
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
                st.rerun()
                # raise Exception('rerun required')
                # if st.button('Refresh apps states'):
                #     st.rerun()
                # ctx = get_script_run_ctx()
                # main_context.script_requests.request_rerun(
                #     RerunData(
                #         query_string=main_context.query_string,
                #         page_script_hash=main_context.page_script_hash,
                #     )
                # )
                # st.empty()
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
        try:
            print('|- kill [{}] {}'.format(child.pid, child.name()), ':iv4s')
            child.kill()
        except psutil.NoSuchProcess:
            pass
    proc.kill()
    print(':i0s')
