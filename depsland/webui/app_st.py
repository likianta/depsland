if __name__ == '__main__':
    __package__ = 'depsland.webui'

import streamlit as st
from streamlit_extras.bottom_container import bottom as st_bottom_bar
from streamlit_extras.row import row as st_row

from . import installed_apps
from . import settings


def get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            'last_command': '',
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
    row = st_row((7, 3), vertical_align='center')
    if appid and (
        _run_at_once or row.button('Install', type='primary')
    ):
        with row.container():
            with st.spinner(f'Installing "{appid}"...'):
                # from time import sleep  # TEST
                # sleep(3)
                from ..api.user_api import install_by_appid
                install_by_appid(appid)


def command_panel() -> None:
    session = get_session()
    with st_bottom_bar():
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
                placeholder=
                session['last_command'] or
                'The command will be executed in the background.',
            )
            if code:
                exec(code, globals())
                session['last_command'] = code


if __name__ == '__main__':
    # strun 3001 depsland/webui/app_st.py
    main('hello_world')
