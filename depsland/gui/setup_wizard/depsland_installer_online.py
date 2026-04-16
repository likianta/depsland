import airmise as air
import streamlit as st
import streamlit_canary as sc
import typing as tp
from argsense import cli

@sc.init_state
class State:
    air_client: tp.Optional[air.Client] = None
    depsland_root = ''
    dirs_index_0 = 0
    # dirs_index_1 = 0
    folders: tp.Dict[str, tp.List[str]] = {}
    installation_path = ''
    temp_hold_dialog_opened = False
    temp_new_folder_name = ''
    __version__ = 15

@cli
def main(client_public_host, client_public_port: int):
    if not State.air_client:
        State.air_client = air.Client(client_public_host, client_public_port)
        State.air_client.open()
        _init_remote_env()
        State.installation_path = _aircall('get_default_installation_path')
    
    st.set_page_config('Online Installing Depsland')
    st.title('Online Installing :red[Depsland]')
    
    _ask_folder()
    if st.button('Install', type='primary', width=160):
        _install_depsland(State.installation_path)
    
    with sc.row('center'):
        if st.button('Refresh remote environment'):
            _init_remote_env()
        if st.button('Test'):
            st.markdown(':green[{}]'.format(_aircall('test', 'Alice')))

@st.fragment
def _ask_folder():
    with st.container(horizontal=True, vertical_alignment='bottom'):
        path = st.text_input(
            'Select folder to install Depsland application',
            State.installation_path,
            help='Input an empty folder or an inexisting folder.'
        )
        if path:
            if _aircall('is_valid_installation_path', path):
                State.depsland_root = path.replace('\\', '/')
            else:
                st.warning(
                    'Please select an **empty** folder or an **inexisting** '
                    'folder to install.'
                )
        # popup st-dialog and show tree view.
        if (
            st.button('Browse', width=120) or
            State.temp_hold_dialog_opened
        ):
            State.temp_hold_dialog_opened = False
            _tree_view()

def _install_depsland(root: str):
    place1 = st.empty()
    prog1 = st.progress(0)
    place2 = st.empty()
    prog2 = st.progress(0)
    
    with place1:
        st.markdown('Downloading Depsland.zip from internet... :gray[wait]')
    with place2:
        st.markdown('Unpacking resources... :gray[wait]')
        
    _airexec(
        '''
        if not fs.exist(root):
            fs.make_dirs(root)
        ''',
        root=root
    )
    
    # @contextmanager
    # def notify_downloading_status():
    #     with place1:
    #         st.markdown(
    #             'Downloading Depsland.zip from internet... :gray[wait]'
    #         )
    #     yield prog1
    #     with place1:
    #         st.markdown(
    #             'Downloading Depsland.zip from internet... :green[done]'
    #         )
    #
    # @contextmanager
    # def notify_extracting_status():
    #     with place2:
    #         st.markdown('Unpacking resources... :gray[wait]')
    #     yield prog2
    #     with place2:
    #         st.markdown('Unpacking resources... :green[done]')
    
    # TEST
    for p, t in _aircall(
        'downloading',
        'http://172.20.128.100:2019/depsland-0.12.0a1.zip',
        root + '/depsland-0.12.0a1.zip',
    ):
        prog1.progress(p, t)
    with place1:
        st.markdown('Downloading Depsland.zip from internet... :green[done]')
    
    for p, t in _aircall(
        'extracting',
        root + '/depsland-0.12.0a1.zip',
        root + '/0.12.0a1',
    ):
        prog2.progress(p, t)
    with place2:
        st.markdown('Unpacking resources... :green[done]')

@st.dialog('Choose Setup Location', width='medium')
def _tree_view():
    """
    ref: $[lib:streamlib_canary/opener.py:file_dialog_st]
    """
    if not State.folders:
        _refresh_tree_model()
    
    place1 = st.empty()
    place2 = st.empty()
    
    def _set_new_folder_name():
        State.temp_new_folder_name = st.session_state['new_folder_input']
    
    with place2:
        with st.container(horizontal=True):
            do_confirm = st.button('Confirm', type='primary')
            do_back = st.button('Back')
            do_enter = st.button('Enter')
            do_refresh = st.button('Refresh tree')
            if st.button('New folder'):
                new_folder_name = st.text_input(
                    'Input folder name',
                    label_visibility='collapsed',
                    key='new_folder_input',
                    on_change=_set_new_folder_name,
                )
            else:
                new_folder_name = State.temp_new_folder_name
                State.temp_new_folder_name = ''
    
    with place1:
        with st.container():
            currdir = st.selectbox(
                'Current location',
                sorted(State.folders.keys()),
                index=State.dirs_index_0,
            )
            
            subdirs = State.folders[currdir]
            if do_refresh:
                subdirs.clear()
            if not subdirs:
                subdirs.extend(_airexec(
                    'return fs.find_dir_names(folder)', folder=currdir
                ))
                
            if new_folder_name:
                if new_folder_name in subdirs:
                    st.toast(
                        ':red[Failed to create new folder: duplicate name!]',
                        duration='long'
                    )
                else:
                    _airexec(
                        'fs.make_dir(path)',
                        path='{}/{}'.format(currdir, new_folder_name)
                    )
                    st.toast(':green[Folder created.]')
                    subdirs.append(new_folder_name)
                    subdirs.sort()
                    State.temp_hold_dialog_opened = True
                    st.rerun()
                    
            with st.container(height=300):
                target_dirname = st.radio('Select folder', subdirs)
                result = '{}/{}'.format(currdir, target_dirname)
            
            def change_dir(dirpath):
                if dirpath not in State.folders:
                    State.folders[dirpath] = []
                    State.dirs_index_0 = sorted(State.folders).index(dirpath)
                    State.temp_hold_dialog_opened = True
                    st.rerun()
            
            if do_back:
                change_dir(currdir.rsplit('/', 1)[0])
            elif do_enter:
                change_dir(result)
            else:
                a, b = result.rsplit('/', 1)
                st.markdown('You selected: **{}/:blue[{}]**'.format(a, b))
    
    if do_confirm:
        State.installation_path = (
            result.endswith('/Depsland') and
            result or
            result + '/Depsland'
        )
        st.rerun()

# ------------------------------------------------------------------------------

def _aircall(func_name: str, *args, **kwargs) -> tp.Any:
    return State.air_client.call(func_name, *args, **kwargs)

def _airexec(code, **kwargs):
    return State.air_client.exec(code, **kwargs)

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

def _refresh_tree_model():
    parent_folders = _airexec(
        '''
        folders = [fs.parent(fs.normpath(os.environ['LOCALAPPDATA']))]

        for root in (
            fs.parent(fs.parent(fs.abspath(sys.argv[0]))),
        ):
            parts = root.split('/')
            temp_list = []
            temp_str = parts[0]
            for p in parts[1:]:
                temp_str += '/' + p
                temp_list.append(temp_str)
            folders.extend(temp_list)
        
        for d in os.listdrives():
            d = d.replace('\\\\', '/')
            folders.append(d)
        
        folders.sort()
        return folders
        '''
    )
    State.folders.clear()
    for i, f in enumerate(parent_folders):
        State.folders[f] = []
        if f.startswith('C:/') and f.endswith('/AppData'):
            State.dirs_index_0 = i

if __name__ == '__main__':
    # 1. see $[./depsland_installer_client_support.py : __main__ : comments]
    # 2. strun 2185 depsland/gui/setup_wizard/depsland_installer_online.py
    #   localhost <client_port>
    cli.run(main)
