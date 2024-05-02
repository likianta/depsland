if __name__ == '__main__':
    __package__ = 'depsland.webui'

import streamlit as st

from . import installed_apps
from . import settings


def main(default_appid: str = '', _run_at_once: bool = False) -> None:
    st.title('Depsland Appinstall')
    
    tabs = st.tabs(('Search & Install', 'Settings'))
    
    with tabs[0]:
        appid = st.text_input(
            'Input an appid to install',
            default_appid,
            placeholder='e.g. "hello_world"'
        )
        cols = st.columns(2)
        if appid and (
            _run_at_once or cols[0].button('Install', type='primary')
        ):
            with cols[1]:
                with st.spinner(f'Installing {appid}...'):
                    # from time import sleep
                    # sleep(3)
                    from ..api.user_api import install_by_appid
                    install_by_appid(appid)
        installed_apps.main()
    with tabs[1]:
        settings.main()


def search_bar(default_appid: str) -> None:
    pass


if __name__ == '__main__':
    # strun 3001 depsland/webui/app_st.py
    main('hello_world')
