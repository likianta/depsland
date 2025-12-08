import typing as t
from contextlib import contextmanager
from random import randint
from time import sleep

import streamlit as st
import streamlit_canary as sc
from lk_utils import Signal

from ...api.user_api.install import detailed_progress

_state: dict = sc.session.get_state(default=lambda: {
    'portion_start': 0.0,
    'portion_end'  : 1.0,
    'progress'     : 0.0,
    'total_count'  : 0,
})


@contextmanager
def progress_bar() -> t.Iterator:
    _prog_ctrl.reset()
    
    placeholder = st.empty()
    with placeholder:
        prog_bar = st.progress(0.0, 'Initializing')
    
    @_prog_ctrl.updated
    def _(prog: float, msg: str) -> None:
        print(':v', msg, f'{prog:.02%}')
        prog_bar.progress(prog, msg)
    
    yield placeholder
    
    # mark done
    prog_bar.progress(1.0, 'Installation done')
    with placeholder:
        st.success('Installation done.')


# noinspection PyProtectedMember
def demo_play() -> None:
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
    
    # callback = progress_bar()
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
        
        @detailed_progress
        def _(
            stage: str, total: int, curr: int, _unused_1, _unused_2, desc: str
        ) -> None:
            if self._last_stage != stage:
                self._change_stage(stage, total)
                self._last_stage = stage
            self.update_progress(curr, desc)
    
    def reset(self) -> None:
        print(':d', 'reset progress bar')
        # if delay: sleep(delay)
        _state.update({
            'portion_start': 0.0,
            'portion_end'  : 1.0,
            'progress'     : 0.0,
            'total_count'  : 0,
        })
        self.updated.emit(0.0, 'Progress reset')
    
    def update_progress(self, count: int, text: str) -> None:
        _state['progress'] = (
            _state['portion_start'] +
            (_state['portion_end'] - _state['portion_start']) *
            (count / _state['total_count'])
        )
        self.updated.emit(_state['progress'], '[{}/{}] {}'.format(
            count, _state['total_count'], text.capitalize()
        ))
    
    def _change_stage(self, stage: str, total_count: int) -> None:
        if stage == 'assets':
            _state.update({
                'portion_start': 0.0,
                'portion_end'  : 0.3,
                'progress'     : 0.0,
                'total_count'  : total_count,
            })
        elif stage == 'deps':
            _state.update({
                'portion_start': 0.3,
                'portion_end'  : 0.8,
                'progress'     : 0.0,
                'total_count'  : total_count,
            })
        elif stage == 'cleanup':
            _state.update({
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
            _state['portion_start'], f'Stage "{stage}" gets started'
        )


_prog_ctrl = ProgressControl()
