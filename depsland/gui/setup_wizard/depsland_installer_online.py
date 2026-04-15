import airmise as air
import streamlit as st
import streamlit_canary as sc
from argsense import cli

@sc.init_state
class State:
    air_client = None
    installation_path = ''
    __version__ = 1

@cli
def main(client_public_host, client_public_port: int):
    if not State.air_client:
        State.air_client = air.Client(client_public_host, client_public_port)
        State.air_client.open()
        State.air_client.exec(
            '''
            import os
            from lk_utils import fs
            
            def get_default_installation_path():
                return os.path.join(os.environ['LOCALAPPDATA'], 'Depsland')
            
            def is_valid_installation_path(path):
                if fs.exist(path):
                    if fs.is_empty_dir(path):
                        return True
                    return False
                return True
            
            return None
            '''
        )
    
    st.set_page_config('Online Installing Depsland')
    st.title('Online Installing :red[Depsland]')
    
    _ask_folder()
    if st.button('Install', type='primary', width=160):
        ...
    
    with sc.row('center'):
        do_test = st.button('Test')
        if do_test:
            st.markdown(':green[{}]'.format(
                _aircall('test', 'Alice')
            ))

@st.fragment
def _ask_folder():
    with st.container(horizontal=True, vertical_alignment='bottom'):
        default_path = _aircall('get_default_installation_path')
        path = st.text_input(
            'Select folder to install Depsland application',
            default_path,
            placeholder=default_path,
            help='Input an empty folder or an inexisting folder.'
        ) or default_path
        if _aircall('is_valid_installation_path', path):
            State.installation_path = path.replace('\\', '/')
        else:
            st.warning(
                'Please select an **empty** folder or an **inexisting** folder '
                'to install.'
            )
        
        st.button('Browse', width=120)  # TODO: popup st-dialog and show tree view.

def _tree_view():
    """
    fetch tree model from client side, render it with
    $[streamlit-arborist @https://github.com/gabriel-msilva/streamlit-arborist].

    ref: https://github.com/gabriel-msilva/streamlit-arborist/blob/main/app/example.py
    """
    # TODO

def _aircall(func_name, *args, **kwargs):
    return State.air_client.call(func_name, *args, **kwargs)

if __name__ == '__main__':
    # 1. see $[./depsland_installer_client_support.py : __main__ : comments]
    # 2. strun 2185 depsland/gui/setup_wizard/depsland_installer_online.py
    #   localhost <client_port>
    cli.run(main)
