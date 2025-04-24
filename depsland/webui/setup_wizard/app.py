if __name__ == '__main__':
    __package__ = 'depsland.webui.setup_wizard'

import typing as t

import streamlit as st
import streamlit_canary as sc
from argsense import cli
from streamlit_extras.bottom_container import bottom as st_bottom_bar

from ..progress_bar import progress_bar
from ...api import install_by_appid

_state = sc.session.init(
    lambda: {'finished': False}
)


@cli
def main(
    app_name: str,
    appid: str,
    description: str = None,
    dry_run: bool = False
) -> None:
    import sys
    print(app_name, appid, dry_run, sys.argv, sys.orig_argv, ':lv')
    
    st.title(f'Installing :blue[{app_name}]...')
    
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
    
    if dry_run:
        _play_demo()
    else:
        if not _state['finished']:
            with progress_bar():
                install_by_appid(appid)
            _state['finished'] = True
        else:
            st.success('Installation done.')
    
    # TODO
    with st_bottom_bar():
        cols = iter(st.columns(2))
        with next(cols):
            sc.long_button('Finish')
        with next(cols):
            sc.long_button('Finish and run', type='primary')


def _play_demo() -> None:
    from lk_utils import wait
    
    def fake_progress() -> t.Iterator[float]:
        for p in wait(3, 50e-3, False):
            yield p.percent
    
    part1 = st.empty()
    with part1:
        st.write('Downloading packages from the internet...')
    prog1 = st.progress(0)
    
    part2 = st.empty()
    with part2:
        st.write('Unpacking packages...')
    prog2 = st.progress(0)
    
    for p in fake_progress():
        prog1.progress(p, '{:.2%}'.format(p))
    with part1:
        st.write('Downloading packages from the internet... :green[done]')
    
    for p in fake_progress():
        prog2.progress(p, '{:.2%}'.format(p))
    with part2:
        st.write('Unpacking packages... :green[done]')


if __name__ == '__main__':
    # strun 2181 depsland/webui/setup_wizard/app.py
    #   -- 'Hello World' hello_world 'Demo play installing hello-world app.'
    #   --dry-run
    # pox -m pyapp_window --port 2181 --size 1010x700
    #   --title 'Depsland Setup Wizard'
    st.set_page_config('Depsland Setup Wizard')
    # main('Hello World', 'hello_world')
    cli.run(main)
