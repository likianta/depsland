import streamlit as st
from random import randint
from time import sleep
from ...api.user_api.install import T
from ...api.user_api.install import install_progress

def start_demo_progress():
    prog_ui = st.progress(0)
    
    for i in range(10):
        prog_ui.progress(
            0.0 + 0.4 * (i + 1) / 10, 'Fetching file #{}'.format(i + 1)
        )
        sleep(randint(1, 5) / 10)  # 100ms ~ 500ms
    
    for i in range(10):
        prog_ui.progress(
            0.4 + 0.5 * (i + 1) / 10, 'Installing package #{}'.format(i + 1)
        )
        sleep(randint(1, 5) / 10)  # 100ms ~ 500ms
    
    for i in range(2):
        prog_ui.progress(
            0.9 + 0.1 * (i + 1) / 10, 'Cleaning stuff #{}'.format(i + 1)
        )
        sleep(randint(5, 10) / 10)  # 500ms ~ 1000ms
    
    prog_ui.progress(1.0, 'Installation done')

def bind_real_progress(signal=install_progress):
    _prog_ui = st.progress(0)
    
    @signal
    def _update_progress(
        stage: T.ProgressStage, percent: float, text: str
    ) -> None:
        if stage == 'updating_assets':
            _prog_ui.progress(0.0 + 0.4 * percent, text)
        elif stage == 'resolving_dependencies':
            _prog_ui.progress(0.4 + 0.5 * percent, text)
        else:
            _prog_ui.progress(0.9 + 0.1 * percent, text)
    
    return _prog_ui
