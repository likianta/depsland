import typing as t
from random import randint
from time import sleep  # noqa

import streamlit as st
from lk_utils import Signal

from ..api.user_api.install import progress


def _get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            'portion_offset': 0.0,
            'portion_weight': 0.0,
            'progress'      : 0.0,
            'total_count'   : 0,
        }
    return st.session_state[__name__]


def make_progress_bar() -> t.Callable[[], None]:
    _prog_ctrl.reset()
    prog_ui = st.progress(0.0, 'Initializing')
    
    @_prog_ctrl.updated
    def _(prog: float, msg: str) -> None:
        prog_ui.progress(prog, msg)
    
    def callback_done() -> None:
        prog_ui.progress(1.0, 'Installation done')
    
    return callback_done


def play_demo() -> None:
    callback = make_progress_bar()
    
    _prog_ctrl.reset()
    _prog_ctrl.session.update({
        'portion_weight': 1.0,
        'total_count'   : 10,
    })
    for i in range(10):
        _prog_ctrl.update_progress(i + 1, target=f'item {i}')
        sleep(randint(1, 5) / 10)  # 100ms ~ 500ms
    
    callback()


class ProgressControl:
    
    def __init__(self) -> None:
        self.updated = Signal(float, str)
        progress.step_updated.bind(self._change_stage)
        progress.prog_updated.bind(self.update_progress)
    
    @property
    def session(self) -> dict:
        return _get_session()
    
    def reset(self) -> None:
        # if delay: sleep(delay)
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
