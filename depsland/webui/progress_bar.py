import typing as t
from random import randint
from time import sleep

import streamlit as st
from lk_utils import Signal

from ..api.user_api.install import progress_updated


def _get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            'portion_start': 0.0,
            'portion_end'  : 1.0,
            'progress'     : 0.0,
            'total_count'  : 0,
        }
    return st.session_state[__name__]


def make_progress_bar() -> t.Callable[[], None]:
    _prog_ctrl.reset()
    
    prog_empty = st.empty()
    with prog_empty:
        prog_ui = st.progress(0.0, 'Initializing')
    
    @_prog_ctrl.updated
    def _(prog: float, msg: str) -> None:
        print(':v', msg, f'{prog:.02%}')
        prog_ui.progress(prog, msg)
    
    def callback_done() -> None:
        prog_ui.progress(1.0, 'Installation done')
        with prog_empty:
            st.success('Installation done')
    
    return callback_done


# noinspection PyProtectedMember
def play_demo() -> None:
    _prog_ctrl.reset()
    
    _prog_ctrl._change_stage('assets', 10)
    for i in range(10):
        _prog_ctrl.update_progress(i + 1, f'fetching file {i}')
        sleep(randint(1, 5) / 10)  # 100ms ~ 500ms
    
    _prog_ctrl._change_stage('deps', 10)
    for i in range(10):
        _prog_ctrl.update_progress(i + 1, f'installing package {i}')
        sleep(randint(1, 5) / 10)  # 100ms ~ 500ms
    
    _prog_ctrl._change_stage('cleanup', 2)
    for i in range(2):
        _prog_ctrl.update_progress(i + 1, f'cleaning stuff {i}')
        sleep(randint(5, 10) / 10)  # 500ms ~ 1000ms
    
    # callback = make_progress_bar()
    # _prog_ctrl.reset()
    # _prog_ctrl.session.update({'total_count': 10})
    # for i in range(10):
    #     print(f'Updating item {i}')
    #     _prog_ctrl.update_progress(i + 1, f'updating item {i}')
    #     sleep(randint(1, 5) / 10)  # 100ms ~ 500ms
    # callback()


class ProgressControl:
    
    def __init__(self) -> None:
        self.updated = Signal(float, str)
        self._last_stage = ''
        
        @progress_updated
        def _(stage: str, total: int, curr: int, text: str) -> None:
            if self._last_stage != stage:
                self._change_stage(stage, total)
                self._last_stage = stage
            self.update_progress(curr, text)
    
    @property
    def session(self) -> dict:
        return _get_session()
    
    def reset(self) -> None:
        print(':d', 'reset progress bar')
        # if delay: sleep(delay)
        self.session.update({
            'portion_start': 0.0,
            'portion_end'  : 1.0,
            'progress'     : 0.0,
            'total_count'  : 0,
        })
        self.updated.emit(0.0, 'Progress reset')
    
    def update_progress(self, count: int, text: str) -> None:
        session = self.session
        session['progress'] = (
            session['portion_start'] +
            (session['portion_end'] - session['portion_start']) *
            (count / session['total_count'])
        )
        self.updated.emit(session['progress'], '[{}/{}] {}'.format(
            count, session['total_count'], text.capitalize()
        ))
    
    def _change_stage(self, stage: str, total_count: int) -> None:
        session = self.session
        if stage == 'assets':
            session.update({
                'portion_start': 0.0,
                'portion_end'  : 0.3,
                'progress'     : 0.0,
                'total_count'  : total_count,
            })
        elif stage == 'deps':
            session.update({
                'portion_start': 0.3,
                'portion_end'  : 0.8,
                'progress'     : 0.0,
                'total_count'  : total_count,
            })
        elif stage == 'cleanup':
            session.update({
                'portion_start': 0.8,
                'portion_end'  : 0.9,
                # ^ 1.0 is reserved for 'installation done'. see also -
                #   `make_progress_bar : callback_done`.
                'progress'     : 0.0,
                'total_count'  : total_count,
            })
        else:
            raise Exception(stage)
        self.updated.emit(
            session['portion_start'], f'Stage "{stage}" gets started'
        )


_prog_ctrl = ProgressControl()
