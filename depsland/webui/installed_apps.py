import typing as t

import psutil
import streamlit as st
from lk_utils import fs

from ..api.user_api import run_app
from ..paths import apps as app_paths


def get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            'progresses': {},  # {appid: pid, ...}
            # 'progresses': {},  # {appid: popen_obj, ...}
        }
    return st.session_state[__name__]


def main() -> None:
    session = get_session()
    cols = st.columns(2)
    colx = -1  # column index
    for app_name, vers in list_installed_apps():
        colx += 1
        with cols[colx % 2]:
            with st.container(border=True):
                is_running = app_name in session['progresses']
                st.write(':blue[**{}**] {}'.format(
                    app_name, '(running)' if is_running else ''
                ))
                target_ver = st.selectbox(
                    'Version ({})'.format(len(vers)),
                    vers,
                    key=f'{app_name}_version',
                )
                
                if is_running:
                    if st.button(
                        ':red[Stop]',
                        key=f'stop_{app_name}',
                        use_container_width=True,
                    ):
                        pid = session['progresses'].pop(app_name)
                        kill_process_tree(pid)
                        # # popen_obj.kill()
                        # # popen_obj.terminate()
                        # os.kill(popen_obj.pid, SIGTERM)
                        # is_killed = popen_obj.poll() is not None
                        # print(
                        #     ':v2' if is_killed else ':v4',
                        #     'popen is {}'.format(
                        #         'killed' if is_killed else 'still alive!'
                        #     )
                        # )
                        st.rerun()
                else:
                    if st.button(
                        ':green[Run]',
                        key=f'run_{app_name}',
                        use_container_width=True,
                    ):
                        popen_obj = run_app(app_name, _version=target_ver)
                        session['progresses'][app_name] = popen_obj.pid
                        st.rerun()


def list_installed_apps() -> t.Iterator[t.Tuple[str, t.List[str]]]:
    for d in fs.find_dirs(app_paths.root):
        if d.name.startswith('.'):
            continue
        if fs.exists(x := f'{d.path}/.inst_history'):
            history = fs.load(x).splitlines()
            yield d.name, history


def kill_process_tree(pid: int) -> None:
    """
    https://stackoverflow.com/questions/70565429/how-to-kill-process-with-
    entire-process-tree-with-python-on-windows
    """
    proc = psutil.Process(pid)
    print('kill [{}] {}'.format(pid, proc.name()), ':iv4s')
    for child in proc.children(recursive=True):
        print('kill [{}:{}] {}'.format(pid, child.pid, child.name()), ':iv4s')
        child.kill()
    proc.kill()
    print(':i0s')
