if __name__ == '__main__':
    __package__ = 'depsland.webui'

import streamlit as st


def main(default_appid: str = '', _run_at_once: bool = False) -> None:
    st.title('Depsland Appinstall')
    appid = st.text_input(
        'Input an appid to install',
        default_appid,
        placeholder='e.g. "hello_world"'
    )
    if appid and (_run_at_once or st.button('Install', type='primary')):
        with st.spinner(f'Installing {appid}...'):
            # from time import sleep
            # sleep(3)
            from ..api.user_api import install_by_appid
            install_by_appid(appid)


if __name__ == '__main__':
    # strun 3001 depsland/webui/app_st.py
    main('hello_world')
