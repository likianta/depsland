if __name__ == '__main__':
    __package__ = 'depsland.webui'

import streamlit as st
import streamlit_nested_layout  # noqa

# from . import bottom_bar
from . import installed_apps
from . import progress_bar
from . import settings
from ..api.user_api.install import install_by_appid
from ..api.self_api import self_upgrade


def _get_session() -> dict:
    if __name__ not in st.session_state:
        st.session_state[__name__] = {
            'placeholder': None,
        }
    return st.session_state[__name__]


def main(default_appid: str = '', _run_at_once: bool = False) -> None:
    # row = st_row((7, 3))
    # with row.container():
    #     st.title('Depsland AppManager')
    # if row.button('Check for updates'):
    #     pass
    st.title('Depsland AppManager')
    tabs = st.tabs(('Search & Install', 'Settings'))
    with tabs[0]:
        search_bar(default_appid, _run_at_once)
        installed_apps.main(_get_session()['placeholder'])
        # bottom_bar.main()
    with tabs[1]:
        settings.main()


def search_bar(default_appid: str, _run_at_once: bool = False) -> None:
    appid = st.text_input(
        'Input an appid to install',
        default_appid,
        placeholder='e.g. "hello_world"'
    ).replace('-', '_')
    
    # main button and a placeholder
    cols = st.columns(2, vertical_alignment='center')
    prog_bar_container = st.container()  # progress bar
    with cols[0]:
        # TODO: how to disable button when installing?
        do_install = st.button(
            'Install', type='primary', disabled=appid == '',
            use_container_width=True
        )
    with cols[1]:
        placeholder = _get_session()['placeholder'] = st.empty()
    
    if appid and (_run_at_once or do_install):
        with prog_bar_container:
            prog_callback = progress_bar.make_progress_bar()
        with placeholder:
            with st.spinner(f'Installing "{appid}"...'):
                # logger = bottom_bar.get_logger()
                # logger.clear()
                # with parallel_printing(logger):
                #     # progress_bar.play_demo()  # TEST
                #     if appid == 'depsland':
                #         self_upgrade()
                #         st.warning('Please restart the app to see the changes.')
                #     else:
                #         install_by_appid(appid)
                #     prog_callback()
                
                if appid == 'depsland':
                    self_upgrade()
                    st.warning('Please restart the app to see the changes.')
                else:
                    install_by_appid(appid)
                prog_callback()


if __name__ == '__main__':
    # strun 3001 depsland/webui/app_st.py
    main('hello_world')
