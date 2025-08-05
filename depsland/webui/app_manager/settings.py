import streamlit as st
from lk_utils import fs

from ... import paths
from ...pypi import rebuild_pypi_index


def main() -> None:
    if st.button('Check for updates'):
        st.write(
            'Please input "depsland" in the search bar and click "Install" '
            'button in main tab.'
        )
    
    with st.expander('System', True):
        add_to_path = st.checkbox(
            'Add to environment PATH',
            help=(
                'Add depsland executable path to environment PATH. \n\n'
                'This allows you to run `depsland` from the command line.'
            )
        )
        # st.caption(
        #     'Add depsland executable path to environment PATH. \n\n'
        #     'This allows you to run `depsland` from the command line.'
        # )
        add_to_desktop = st.checkbox('Create desktop shortcut')
        
    with st.expander('Development', True):
        dir_i = st.text_input(
            'Third party libraries',
            placeholder='Input a directory path.',
            help='Depsland will collect package files (*.whl, *.tar.gz, etc.) '
                 'in this folder to rebuil pypi index.'
        )
        if dir_i and fs.exist(dir_i):
            with st.spinner('Indexing...'):
                dir_o = paths.pypi.downloads
                for f in fs.find_files(dir_i):
                    file_i = f.path
                    file_o = '{}/{}'.format(dir_o, f.name)
                    if not fs.exist(file_o):
                        fs.make_link(file_i, file_o)
                rebuild_pypi_index(perform_pip_install=True)
    
    if st.button('Apply settings', type='primary', use_container_width=True):
        print(add_to_path, add_to_desktop)
        st.success('Settings applied.')
