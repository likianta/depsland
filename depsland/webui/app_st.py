if __name__ == '__main__':
    __package__ = 'depsland.webui'

from time import sleep

import streamlit as st
from lk_utils import Signal
# from lk_utils import run_new_thread
from streamlit_extras.bottom_container import bottom as st_bottom_bar

from . import installed_apps
from . import settings
from ..api.user_api.install import install_by_appid
from ..api.user_api.install import progress


def get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            'last_command'  : '',
            # progress indicator
            'portion_offset': 0.0,
            'portion_weight': 0.0,
            'progress'      : 0.0,
            'total_count'   : 0,
        }
    return st.session_state[__name__]


def main(default_appid: str = '', _run_at_once: bool = False) -> None:
    st.title('Depsland Appinstall')
    
    tabs = st.tabs(('Search & Install', 'Settings'))
    
    with tabs[0]:
        search_bar(default_appid, _run_at_once)
        installed_apps.main()
        command_panel()
    
    with tabs[1]:
        settings.main()


def search_bar(default_appid: str, _run_at_once: bool = False) -> None:
    appid = st.text_input(
        'Input an appid to install',
        default_appid,
        placeholder='e.g. "hello_world"'
    )
    
    row0 = st.columns(2)
    row1 = st.container()
    
    # with row0[0]:
    #     do_install = st.button(
    #         'Install', type='primary', use_container_width=True)
    
    if appid and (_run_at_once or row0[0].button(
        'Install', type='primary', use_container_width=True
    )):
        with row1:
            _prog_ctrl.reset()
            prog_ui = st.progress(0.0, f'Installing "{appid}"')
            
            @_prog_ctrl.updated
            def _(prog: float, msg: str) -> None:
                prog_ui.progress(prog, msg)
        
        with row0[1]:
            with st.spinner(f'Installing "{appid}"...'):
                install_by_appid(appid)
                # _test_install_progress()  # TEST
                prog_ui.progress(1.0, 'Installation done')
                # run_new_thread(_prog_ctrl.reset, args=(3,))


def command_panel() -> None:  # the bottom bar
    with st_bottom_bar():
        with st.expander('Command panel', False):
            session = get_session()
            containers = (st.container(), st.container())
            with containers[1]:
                if st.checkbox('Remember last input', True):
                    value = session['last_command'] or None
                else:
                    value = None
            with containers[0]:
                code = st.text_area(
                    'Command here',
                    value=value,
                    placeholder=(
                        session['last_command'] or
                        'The command will be executed in the background.'
                    ),
                )
                if code:
                    exec(code, globals())
                    session['last_command'] = code


def _test_install_progress() -> None:
    from random import randint
    _prog_ctrl.reset()
    _prog_ctrl.session.update({
        'portion_weight': 1.0,
        'total_count'   : 10,
    })
    for i in range(10):
        _prog_ctrl.update_progress(i + 1, target=f'item {i}')
        sleep(randint(1, 5) / 10)  # 100ms ~ 500ms


class ProgressControl:
    
    def __init__(self) -> None:
        self.updated = Signal(float, str)
        progress.step_updated.bind(self._change_stage)
        progress.prog_updated.bind(self.update_progress)
    
    @property
    def session(self) -> dict:
        return get_session()
    
    def reset(self, delay: int = 0) -> None:
        if delay: sleep(delay)
        self.session.update({
            'portion_offset': 0.0,
            'portion_weight': 0.0,
            'progress'      : 0.0,
            'total_count'   : 0,
        })
        self.updated.emit(0.0, 'Progress reset')
    
    def update_progress(self, counter: int, target: str) -> None:
        session = self.session
        session['progress'] = (
            session['portion_offset'] +
            session['portion_weight'] * (counter / session['total_count'])
        )
        self.updated.emit(session['progress'], f'Updating {target}')
        # sleep(0.5)  # TEST: slow down the motion to see the progress bar
    
    def _change_stage(self, stage: str, total_count: int) -> None:
        session = self.session
        if stage == 'assets':
            session.update({
                'portion_offset': 0.0,
                'portion_weight': 0.4,
                'progress'      : 0.0,
                'total_count'   : total_count,
            })
        elif stage == 'dependencies':
            session.update({
                'portion_offset': 0.4,
                'portion_weight': 0.6,
                'progress'      : 0.0,
                'total_count'   : total_count,
            })
        else:
            raise Exception
        self.updated.emit(
            session['portion_offset'], f'Stage "{stage}" get started'
        )
        # sleep(3)  # TEST: slow down the motion to see the progress bar


_prog_ctrl = ProgressControl()

if __name__ == '__main__':
    # strun 3001 depsland/webui/app_st.py
    main('hello_world')
