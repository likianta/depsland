import airmise as air
import streamlit as st
import streamlit_canary as sc
import typing as tp
from argsense import cli
from streamlit_arborist import tree_view

@sc.init_state
class State:
    air_client: tp.Optional[air.Client] = None
    depsland_root = ''
    tree_model = []
    __version__ = 3

@cli
def main(client_public_host, client_public_port: int):
    if not State.air_client:
        State.air_client = air.Client(client_public_host, client_public_port)
        State.air_client.open()
        _init_remote_env()
    
    st.set_page_config('Online Installing Depsland')
    st.title('Online Installing :red[Depsland]')
    
    _ask_folder()
    if st.button('Install', type='primary', width=160):
        _install_depsland()
    
    with sc.row('center'):
        if st.button('Test'):
            st.markdown(':green[{}]'.format(_aircall('test', 'Alice')))
        if st.button('Refresh remote environment'):
            _init_remote_env()

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
            State.depsland_root = path.replace('\\', '/')
        else:
            st.warning(
                'Please select an **empty** folder or an **inexisting** folder '
                'to install.'
            )
        
        # popup st-dialog and show tree view.
        if st.button('Browse', width=120):
            _tree_view()

def _install_depsland():
    place1 = st.empty()
    prog1 = st.progress(0)
    place2 = st.empty()
    prog2 = st.progress(0)
    
    with place1:
        st.markdown(
            'Downloading Depsland package from internet... :gray[wait]'
        )
    with place2:
        st.markdown('Unpacking resources... :gray[wait]')
    
    # TEST
    for p, t in _aircall(
        'downloading',
        'http://172.20.128.100:2019/depsland-0.12.0a1.zip',
        State.depsland_root + '/depsland-0.12.0a1.zip',
    ):
        prog1.progress(p, t)
    with place1:
        st.markdown(
            'Downloading Depsland package from internet... :green[done]'
        )
        
    for p, t in _aircall(
        'extracting',
        State.depsland_root + '/depsland-0.12.0a1.zip',
        State.depsland_root + '/0.12.0a1',
    ):
        prog2.progress(p, t)
    with place2:
        st.markdown('Unpacking resources... :green[done]')

@st.dialog('Setup location', width='medium')
def _tree_view():
    """
    fetch tree model from client side, render it with
    $[streamlit-arborist @https://github.com/gabriel-msilva/streamlit-arborist].

    ref: https://github.com/gabriel-msilva/streamlit-arborist/blob/main/app/example.py
    """
    if not State.tree_model:
        _refresh_tree_model()

    if st.button('Refresh tree model'):
        _refresh_tree_model()
        
    result = tree_view(
        State.tree_model,
        open_by_default=True,
    )
    print(result)

def _refresh_tree_model():
    with st.spinner('Initializing tree model...'):
        possible_parent_folders = State.air_client.exec(
            '''
            return (
                os.environ['LOCALAPPDATA'],
                os.path.abspath(os.path.dirname(sys.argv[0])),
            )
            '''
        )
        State.tree_model = State.air_client.exec(
            '''
            def get_tree_model(parent_folders):
                id = 0
    
                def recurse(folder, current_depth):
                    nonlocal id
                    if current_depth > 3:
                        return []
                    out = []
                    for d in fs.find_dirs(folder):
                        id += 1
                        out.append({
                            'id': str(id),
                            'name': d.name,
                            'children': recurse(d.path, current_depth + 1)
                        })
                    return out
    
                out = []
                for root in parent_folders:
                    id += 1
                    if root == os.environ['LOCALAPPDATA']:
                        # do not dive into this folder because subfolders
                        # require promoting privileges.
                        out.append({
                            'id': str(id),
                            'name': root,
                            'children': []
                        })
                    else:
                        out.append({
                            'id': str(id),
                            'name': root,
                            'children': recurse(root, 0)
                        })
                return out
    
            return get_tree_model(parent_folders)
            ''',
            parent_folders=possible_parent_folders,
        )

# ------------------------------------------------------------------------------

def _aircall(func_name: str, *args, **kwargs) -> tp.Any:
    return State.air_client.call(func_name, *args, **kwargs)

def _init_remote_env():
    State.air_client.exec(
        '''
        import os
        import sys
        from lk_utils import fs
        from lk_utils import run_new_thread
        from time import sleep

        def downloading(url, path):
            progress = (0.0, '0%')
            progress_done = False

            def _update_progress(prog):
                nonlocal progress, progress_done
                progress = (prog.percent, '{} ({:.2%})'.format(
                    _pretty_size(prog.total), prog.percent
                ))
                progress_done = prog.percent >= 1
            
            def _pretty_size(value):
                return '{:.2f}MB'.format(value / 1024 / 1024)

            run_new_thread(
                fs.download,
                url,
                path,
                keep_file=True,
                progress=_update_progress,
                overwrite=True,
            )

            while not progress_done:
                yield progress
                sleep(0.1)
        
        def extracting(file_zip, folder):
            progress = (0.0, '')
            progress_done = False

            def _update_progress(prog):
                nonlocal progress, progress_done
                progress = (prog.percent, '[{}/{}] {} ({:.2%})'.format(
                    prog.index,
                    prog.total,
                    prog.text.rsplit('/', 1)[-1]),
                    prog.percent
                )
                progress_done = prog.percent >= 1

            run_new_thread(
                fs.unzip_file,
                file_zip,
                folder,
                progress=_update_progress,
                overwrite=False,
            )

            while not progress_done:
                yield progress
                sleep(0.1)
        
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

if __name__ == '__main__':
    # 1. see $[./depsland_installer_client_support.py : __main__ : comments]
    # 2. strun 2185 depsland/gui/setup_wizard/depsland_installer_online.py
    #   localhost <client_port>
    cli.run(main)
