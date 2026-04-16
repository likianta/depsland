import airmise as air
import streamlit as st
import streamlit_canary as sc
import typing as tp
from argsense import cli
from contextlib import contextmanager

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
    __version__ = 18

@cli
def main(
    client_public_host: str,
    client_public_port: int,
    target_appid: str = '',
    # target_name: str = '',
    target_version: str = '',
) -> None:
    # if target_appid:
    #     assert target_name and target_version
    
    if not State.air_client:
        State.air_client = air.Client(client_public_host, client_public_port)
        State.air_client.open()
        _init_remote_env()
        State.installation_path = _aircall('get_default_installation_path')
    
    st.set_page_config('Online Installing Depsland')
    st.title('Online Installing :red[Depsland]')
    
    _ask_folder()
    
    if st.button('Install', type='primary', width=160):
        depsland_direct_path = _install_depsland(State.installation_path)
        if target_appid:
            _install_target_application(
                depsland_direct_path, target_appid, target_version
            )
    
    with sc.row('center'):
        if st.button('Refresh remote environment'):
            _init_remote_env()
        if st.button('Test'):
            st.markdown(':green[{}]'.format(_aircall('test', 'Alice')))

@st.fragment
def _ask_folder():
    place1 = st.empty()
    place2 = st.empty()
    
    def _sync_manual_path_setting():
        State.installation_path = st.session_state[
            'install_path_input:{}'.format(State.installation_path)
        ]
    
    with place1:
        with st.container(horizontal=True, vertical_alignment='bottom'):
            path = st.text_input(
                'Select folder to install Depsland application',
                State.installation_path,
                key='install_path_input:{}'.format(State.installation_path),
                on_change=_sync_manual_path_setting,
                help='Input an empty folder or an inexisting folder.',
            )
            if path:
                if _aircall('is_valid_installation_path', path):
                    State.installation_path = path.replace('\\', '/')
                else:
                    with place2:
                        st.warning(
                            'Please select an **empty** folder or an '
                            '**inexisting** folder to install.'
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
    label1 = ':one: Downloading Depsland.zip from internet...'
    prog1 = st.progress(0)
    place2 = st.empty()
    label2 = ':two: Unpacking resources...'
    prog2 = st.progress(0)
    
    with place1:
        st.markdown(label1 + ' :gray[wait]')
    with place2:
        st.markdown(label2 + ' :gray[wait]')
    
    _airexec(
        '''
        if not fs.exist(root):
            fs.make_dirs(root)
        ''',
        root=root
    )
    
    @contextmanager
    def notify_downloading_status():
        with place1:
            st.markdown(label1)
        yield prog1
        with place1:
            st.markdown(label1 + ' :green[done]')
        prog1.progress(1.0, 'Depsland downloaded')

    @contextmanager
    def notify_extracting_status():
        with place2:
            st.markdown(label2)
        yield prog2
        with place2:
            st.markdown(label2 + ' :green[done]')
        prog2.progress(1.0, 'Depsland extracted')

    # TEST
    with notify_downloading_status() as prog:
        for p, t in _aircall(
            'downloading',
            'http://172.20.128.100:2019/depsland-0.12.0a2.zip',
            root + '/depsland-0.12.0a2.zip',
        ):
            print(p, t, ':iv')
            prog.progress(p, t)
    
    with notify_extracting_status() as prog:
        for p, t in _aircall(
            'extracting',
            root + '/depsland-0.12.0a2.zip',
            root + '/0.12.0a2',
        ):
            print(p, t, ':iv')
            prog.progress(p, t)
    
    return root + '/0.12.0a2'

def _install_target_application(depsland_root, appid, version):
    place1 = st.empty()
    label1 = ':three: Downloading target application assets...'
    prog1 = st.progress(0)
    place2 = st.empty()
    label2 = ':four: Resolving target application dependencies...'
    prog2 = st.progress(0)
    place3 = st.empty()
    label3 = ':five: Finishing target application...'
    prog3 = st.progress(0)
    
    with place1:
        st.markdown(label1 + ' :gray[wait]')
    with place2:
        st.markdown(label2 + ' :gray[wait]')
    with place3:
        st.markdown(label3 + ' :gray[wait]')
    
    generator = _airexec(
        '''
        def run_depsland_install(depsland_root, appid, version):
            if depsland_root not in sys.path:
                sys.path.insert(0, depsland_root)
                sys.path.insert(1, depsland_root + '/chore/site_packages')
            
            if 'depsland' in sys.modules:
                sys.modules.pop('depsland')
            import depsland
            print(depsland.__path__)
            
            from depsland.api.user_api import install_by_appid
            from depsland.api.user_api import install_progress
            
            progress = ('', 0.0, '')
            progress_done = False
            
            @install_progress.bind
            def _update_progress(stage, percent, text):
                nonlocal progress, progress_done
                progress = (stage, percent, text)
                progress_done = stage == 'ending' and percent >= 1
            
            run_new_thread(install_by_appid, appid, version)
            
            while not progress_done:
                yield progress
                sleep(0.1)
            yield (progress[0], 1.0, progress[2])
        
        return run_depsland_install(depsland_root, appid, version)
        ''',
        depsland_root=depsland_root,
        appid=appid,
        version=version,
    )
    
    # @contextmanager
    # def notify_stage1_status():
    #     with place1:
    #         st.markdown(label1)
    #     yield prog1
    #     with place1:
    #         st.markdown(label1 + ' :green[done]')
    #
    # @contextmanager
    # def notify_stage2_status():
    #     with place2:
    #         st.markdown(label2)
    #     yield prog2
    #     with place2:
    #         st.markdown(label2 + ' :green[done]')
    #
    # @contextmanager
    # def notify_stage3_status():
    #     with place3:
    #         st.markdown(label3)
    #     yield prog3
    #     with place3:
    #         st.markdown(label3 + ' :green[done]')
    
    curr_prog = prog1
    last_stage = ''
    for stage, percent, text in generator:
        if last_stage != stage:
            if stage == 'updating_assets':
                with place1:
                    st.markdown(label1)
                curr_prog = prog1
            elif stage == 'resolving_dependencies':
                with place1:
                    st.markdown(label1 + ' :green[done]')
                prog1.progress(1.0, 'All assets downloaded')
                with place2:
                    st.markdown(label2)
                curr_prog = prog2
            else:
                with place2:
                    st.markdown(label2 + ' :green[done]')
                prog2.progress(1.0, 'All dependencies resolved')
                with place3:
                    st.markdown(label3)
                curr_prog = prog3
            last_stage = stage
        curr_prog.progress(percent, text)
    else:
        with place3:
            st.markdown(label3 + ' :green[done]')
        prog3.progress(1.0, 'Finished miscellaneous stuff')

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
            progress = (0.0, '')
            progress_done = False

            def _update_progress(prog):
                nonlocal progress, progress_done
                progress = (
                    prog.percent,
                    '{} ({:.2%})'.format(
                        _pretty_size(prog.total), prog.percent
                    )
                )
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
            yield (1.0, progress[1])
        
        def extracting(file_zip, folder):
            progress = (0.0, '')
            progress_done = False

            def _update_progress(prog):
                nonlocal progress, progress_done
                progress = (
                    prog.percent,
                    '[{}/{}] {}'.format(
                        prog.index,
                        prog.total,
                        prog.text.rsplit('/', 1)[-1],
                        # prog.percent
                    )
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
            yield (1.0, progress[1])
        
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
    # 2.a.
    #   strun 2185 depsland/gui/setup_wizard/depsland_installer_online.py
    #   localhost <client_port>
    # 2.b.
    #   strun 2185 depsland/gui/setup_wizard/depsland_installer_online.py
    #   localhost <client_port> hello_world_tkinter <version>
    cli.run(main)
