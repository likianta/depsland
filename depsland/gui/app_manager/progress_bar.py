import streamlit as st
from contextlib import contextmanager
from random import randint
from time import sleep
from ...api.user_api.install import T
from ...api.user_api.install import install_progress

@contextmanager
def start_demo_progress():
    prog_ui = st.progress(0)
    
    for i in range(10):
        prog_ui.progress(
            0.0 + 0.3 * (i + 1) / 10, 'Fetching file #{}'.format(i + 1)
        )
        sleep(randint(1, 5) / 10)  # 100ms ~ 500ms
    
    for i in range(10):
        prog_ui.progress(
            0.3 + 0.5 * (i + 1) / 10, 'Installing package #{}'.format(i + 1)
        )
        sleep(randint(1, 5) / 10)  # 100ms ~ 500ms
    
    for i in range(2):
        prog_ui.progress(
            0.8 + 0.2 * (i + 1) / 10, 'Cleaning stuff #{}'.format(i + 1)
        )
        sleep(randint(5, 10) / 10)  # 500ms ~ 1000ms
    
    yield prog_ui

    prog_ui.progress(1.0, 'Installation done')

@contextmanager
def start_real_progress(progress_signal=install_progress):
    _prog_ui = st.progress(0)
    
    @progress_signal.bind
    def _update_progress(
        stage: T.ProgressStage, percent: float, text: str
    ) -> None:
        match stage:
            case 'updating_assets':  # 30%
                _prog_ui.progress(0.0 + 0.3 * percent, text)
            case 'resolving_dependencies':  # 40%
                _prog_ui.progress(0.3 + 0.4 * percent, text)
            case 'linking_dependencies':  # 20%
                _prog_ui.progress(0.7 + 0.2 * percent, text)
            case 'ending':  # 10%
                _prog_ui.progress(0.9 + 0.1 * percent, text)
    
    yield _prog_ui
    
    _prog_ui.progress(1.0, 'Installation done')
