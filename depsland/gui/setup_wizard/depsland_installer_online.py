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
    folders: tp.Dict[str, tp.List[str]] = {}
    installation_done = False
    installation_path = ''
    target: tp.Optional[tp.Tuple[str, str]] = None
    temp_hold_dialog_opened = False
    temp_new_folder_name = ''
    tree_select_index_0 = 0
    tree_select_index_1 = 0
    __version__ = 22

@cli
def main(
    debug: bool = False,
    **kwargs
    # client_public_host: tp.Optional[str] = None,
    # client_public_port: tp.Optional[int] = None,
    # target_appid: tp.Optional[str] = None,
    # target_version: tp.Optional[str] = None,
) -> None:
    st.set_page_config('Online Installing Depsland')
    st.title('Online Installing :red[Depsland]')

    if not State.air_client:
        if debug:
            client_public_host = kwargs['client_public_host']
            client_public_port = kwargs['client_public_port']
            target_appid = kwargs.get('target_appid', '')
            target_version = kwargs.get('target_version', '')
        else:
            # the incoming url should be like: 
            # $[http://<host>:<port>/?client-open-port=<open_port>
            # &target-appid=<appid>&target-version=<version>] $[// target-* are 
            # optional]
            if st.query_params:
                client_public_host = 'localhost'
                client_public_port = int(st.query_params['client-open-port'])
                target_appid = st.query_params.get('target-appid', '')
                target_version = st.query_params.get('target-version', '')
            else:
                st.warning('Invalid query parameter.')
                return
        if target_appid and target_version:
            State.target = (target_appid, target_version)

        State.air_client = air.Client(client_public_host, client_public_port)
        State.air_client.open()
        _init_remote_env()
        State.installation_path = _aircall('get_default_installation_path')
    
    if not State.installation_done:
        _ask_folder()
    
    with st.container(horizontal=True):
        do_inst = st.button(
            'Install', 
            type='primary', 
            width=160, 
            disabled=State.installation_done
        )
        do_close_place = st.empty()
    above_progress_place = st.empty()
    if do_inst:
        with st.expander('Installation progress', True):
            depsland_direct_path = _install_depsland(
                State.installation_path
            )
            if State.target:
                _install_target_application(
                    depsland_direct_path, *State.target
                )
            State.installation_done = True
            # State.air_client.close()
    if State.installation_done:
        with above_progress_place:
            st.success(
                'Installation done. You can now close this window and rerun '
                'the same ".exe" file to launch target application.'
            )
        with do_close_place:
            st.button(':red[Close this window/tab]', on_click=_close_tab_2)
    
    if debug:
        with sc.row('center'):
            if st.button('Refresh remote environment'):
                _init_remote_env()
            if st.button('Test'):
                st.markdown(':green[{}]'.format(_aircall('test', 'Alice')))
            # if st.button(':red[Force close]'):
            #     State.air_client.close()
            if st.button(':red[Close this tab]'):
                _close_tab_2()

@st.fragment
def _ask_folder() -> None:
    place1 = st.empty()
    place2 = st.empty()
    
    def _sync_manual_path_setting() -> None:
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
                help=(
                    '''
                    If input an empty folder or a non-existent folder path, will 
                    use it as installation path.

                    If input a non-empty folder path, will use 
                    `<the_given_path>/Depsland` as installation path.

                    There is a trick: you can input a path to a ".zip" file, 
                    which is a [Depsland Standalone package]({}); the program 
                    will then treat it as downloaded resource and continue 
                    installation.
                    '''.format(
                        'http://172.20.128.100:2188/'
                        'depsland_online_installer.zip'
                    )
                ),
            )
            if path:
                path = path.replace('\\', '/')
                if path.endswith('.zip'):
                    State.installation_path = path
                elif _aircall('is_empty_folder', path):
                    State.installation_path = path
                else:
                    path += '/Depsland'
                    if _aircall('is_empty_folder', path):
                        with place2:
                            st.warning(
                                'Please select an **empty** folder or an '
                                '**inexisting** folder to install.'
                            )
                    else:
                        State.installation_path = path
                print(State.installation_path)
            
            # popup st-dialog and show tree view.
            if (
                st.button('Browse', width=120) or
                State.temp_hold_dialog_opened
            ):
                State.temp_hold_dialog_opened = False
                _tree_view()

def _close_tab_1() -> None:
    # FIXME: doesn't work.
    st.html(
        '<script>window.close();</script>', 
        unsafe_allow_javascript=True
    )
    State.air_client.close()

def _close_tab_2() -> None:
    # simulate `ctrl + w` in client side using only standard python libraries.
    _airexec(
        '''
        # https://github.com/gauthsvenkat/pyKey/blob/master/pyKey/windows.py
        # https://chatgpt.com/share/69e5b8d8-1578-8320-9a9d-40f07d28fd88
        
        import ctypes
        from ctypes import wintypes
        from time import sleep

        def simulate_ctrl_w():
            # C struct redefinitions 
            PUL = ctypes.POINTER(ctypes.c_ulong)

            class KeyBdInput(ctypes.Structure):
                _fields_ = (
                    ("wVk", ctypes.c_ushort),
                    ("wScan", ctypes.c_ushort),
                    ("dwFlags", ctypes.c_ulong),
                    ("time", ctypes.c_ulong),
                    ("dwExtraInfo", PUL)
                )

            class HardwareInput(ctypes.Structure):
                _fields_ = (
                    ("uMsg", ctypes.c_ulong),
                    ("wParamL", ctypes.c_short),
                    ("wParamH", ctypes.c_ushort)
                )

            class MouseInput(ctypes.Structure):
                _fields_ = (
                    ("dx", ctypes.c_long),
                    ("dy", ctypes.c_long),
                    ("mouseData", ctypes.c_ulong),
                    ("dwFlags", ctypes.c_ulong),
                    ("time",ctypes.c_ulong),
                    ("dwExtraInfo", PUL)
                )

            class Input_I(ctypes.Union):
                _fields_ = (
                    ("ki", KeyBdInput),
                    ("mi", MouseInput),
                    ("hi", HardwareInput)
                )

            class Input(ctypes.Structure):
                _fields_ = (
                    ("type", ctypes.c_ulong),
                    ("ii", Input_I)
                )
            
            # https://github.com/gauthsvenkat/pyKey/blob/master/pyKey/key_dict.py
            _key_dict = {'CTRL': 0x1D, 'W': 0x11}
            _send_input = ctypes.windll.user32.SendInput

            def key_down(key: str):
                extra = ctypes.c_ulong(0)
                ii_ = Input_I()
                ii_.ki = KeyBdInput(
                    0, _key_dict[key], 0x0008, 0, ctypes.pointer(extra)
                )
                x = Input(ctypes.c_ulong(1), ii_)
                _send_input(1, ctypes.pointer(x), ctypes.sizeof(x))

            def key_up(key: str):
                extra = ctypes.c_ulong(0)
                ii_ = Input_I()
                ii_.ki = KeyBdInput(
                    0, _key_dict[key], 0x0008 | 0x0002, 0, ctypes.pointer(extra)
                )
                x = Input( ctypes.c_ulong(1), ii_ )
                _send_input(1, ctypes.pointer(x), ctypes.sizeof(x))
            
            key_down('CTRL')
            key_down('W')
            sleep(0.02)
            key_up('W')
            key_up('CTRL')

        simulate_ctrl_w()
        '''
    )
    State.air_client.close()

def _install_depsland(root: str) -> str:
    """
    trick: if root is a path to zip file, we will skip downloading process.
    """
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
    
    if root.endswith('.zip'):
        print('skip downloading depsland.zip because we use cached file.')
        temp = root
        path0 = temp.rsplit('/', 1)[0]
        path1 = temp
        path2 = path0 + '/0.12.0a3'
    else:
        path0 = root
        path1 = root + '/depsland-0.12.0a3.zip'
        path2 = root + '/0.12.0a3'
        _airexec(
            '''
            if not fs.exist(root):
                fs.make_dirs(root)
            ''',
            root=path0
        )

    @contextmanager
    def notify_downloading_status() -> tp.Iterator[st.progress]:
        with place1:
            st.markdown(label1)
        yield prog1
        with place1:
            st.markdown(label1 + ' :green[done]')
        prog1.progress(1.0, 'Depsland downloaded')

    @contextmanager
    def notify_extracting_status() -> tp.Iterator[st.progress]:
        with place2:
            st.markdown(label2)
        yield prog2
        with place2:
            st.markdown(label2 + ' :green[done]')
        prog2.progress(1.0, 'Depsland extracted')

    with notify_downloading_status() as prog:
        if root.endswith('.zip'):
            prog.progress(1.0, 'Depsland already downloaded.')
        else:
            for p, t in _aircall(
                'downloading',
                'http://172.20.128.100:2188/depsland-0.12.0a3.zip',
                path1,
            ):
                # print(p, t, ':iv')
                prog.progress(p, t)
    
    with notify_extracting_status() as prog:
        for p, t in _aircall('extracting', path1, path2):
            # print(p, t, ':iv')
            prog.progress(p, t)
    return path2

def _install_target_application(
    depsland_root: str, appid: str, version: str
) -> None:
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
                result = (
                    target_dirname is None and currdir or
                    '{}/{}'.format(currdir, target_dirname)
                )
            
            def change_dir(dirpath):
                if dirpath not in State.folders:
                    State.folders[dirpath] = []
                State.dirs_index_0 = sorted(State.folders).index(dirpath)
                State.temp_hold_dialog_opened = True
                st.rerun()
            
            if do_back:
                change_dir(currdir.rsplit('/', 1)[0])
            elif do_enter and result != currdir:
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

        def is_empty_folder(path: str) -> bool:
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
            break

if __name__ == '__main__':
    # see `./readme.mo : Demo Run : Start GUI with debug arguments`
    cli.run(main)
