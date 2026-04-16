if __name__ == '__main__':
    __package__ = 'depsland.gui.setup_wizard'

import streamlit as st
import streamlit_canary as sc
from airmise import Client as AirClient
from argsense import cli
from streamlit_extras.bottom_container import bottom as bottom_container
from ..app_manager.progress_bar import bind_real_progress
from ..app_manager.progress_bar import start_demo_progress
from ...api import install_by_appid

state = sc.init_state(lambda: {
    'air_client': None,
    'finished': False,
})

@cli
def main(
    app_name: str,
    appid: str,
    description: str = None,
    dry_run: bool = False,
    emit_close_event: bool = False,
) -> None:
    # print(app_name, appid, dry_run, emit_close_event, ':lv')
    st.set_page_config('Depsland Setup Wizard')
    
    if emit_close_event:
        if not state['air_client']:
            state['air_client'] = AirClient(port=2184)
            state['air_client'].open()
            state['air_client'].call('start')
    
    with st.sidebar:
        st.image('chore/setup_wizard_logo.png')
        # st.subheader(app_name)
        st.markdown(
            '<h2 style="text-align: center; color: black;">{}</h2>'
            .format(app_name),
            unsafe_allow_html=True,
        )
        if description:
            st.divider()
            st.markdown(description)
    
    if state['finished']:
        st.title(app_name)
        st.success(
            'Installation done.\n\n'
            'You can now close this window and restart the same app again, '
            'there will launch target app instead of wizard.'
        )
        if emit_close_event:
            with bottom_container():
                with st.container(horizontal=True):
                    if dry_run:
                        if st.button('Play again'):
                            state['finished'] = False
                            st.rerun()
                    if st.button(
                        'Finish', type='secondary', width='stretch'
                    ):
                        state['air_client'].call('close', False)
                    if st.button(
                        'Finish and run', type='primary', width='stretch'
                    ):
                        state['air_client'].call('close', True)
    else:
        st.title(f'Installing :blue[{app_name}]...')
        if dry_run:
            start_demo_progress()
        else:
            prog_ui = bind_real_progress()
            install_by_appid(appid)
            prog_ui.progress(1.0, 'Installation done')
        state['finished'] = True
        st.rerun()

# def _demo_play() -> None:
#     from lk_utils import wait
#
#     def fake_progress() -> t.Iterator[float]:
#         for p in wait(3, 50e-3, False):
#             yield p.percent
#
#     part1 = st.empty()
#     with part1:
#         st.write('Downloading packages from the internet...')
#     prog1 = st.progress(0)
#
#     part2 = st.empty()
#     with part2:
#         st.write('Unpacking packages...')
#     prog2 = st.progress(0)
#
#     for p in fake_progress():
#         prog1.progress(p, '{:.2%}'.format(p))
#     with part1:
#         st.write('Downloading packages from the internet... :green[done]')
#
#     for p in fake_progress():
#         prog2.progress(p, '{:.2%}'.format(p))
#     with part2:
#         st.write('Unpacking packages... :green[done]')

if __name__ == '__main__':
    # strun 2183 depsland/gui/setup_wizard/setup_wizard.py 'Hello World'
    #   hello_world 'Demo play installing hello-world app.' :true
    # pox -m pyapp_window -p 2183 -s 870x590 -t `Hello World Example`
    cli.run(main)
