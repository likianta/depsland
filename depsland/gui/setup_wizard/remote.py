import typing as tp

import airmise as air
import streamlit as st
import streamlit_canary as sc


@sc.init_state
class State:
    air_client: tp.Optional[air.Client] = None
    folders: tp.Dict[str, tp.List[str]] = {}
    temp_hold_dialog_opened = False
    temp_new_folder_name = ''
    tree_select_index_0 = 0
    tree_select_index_1 = 0


def aircall(func_name: str, *args, **kwargs) -> tp.Any:
    return State.air_client.call(func_name, *args, **kwargs)


def airexec(code, **kwargs):
    return State.air_client.exec(code, **kwargs)


def close_air_client() -> None:
    if State.air_client:
        State.air_client.close()


def init_air_client(
    debug: bool = False, **kwargs
) -> tp.Optional[tp.Tuple[str, str]]:
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
            st.stop()

    State.air_client = air.Client(client_public_host, client_public_port)
    State.air_client.open()

    _init_remote_env()

    return (
        (target_appid, target_version)
        if target_appid and target_version
        else None
    )


@st.dialog('Choose Setup Location', width='medium')
def tree_view() -> None:
    """
    ref: `lib:streamlib_canary/opener.py:file_dialog_st`
    """
    if not State.folders:
        _refresh_tree_model()

    place1 = st.empty()
    place2 = st.empty()

    def _set_new_folder_name() -> None:
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
                index=State.tree_select_index_0,
            )

            subdirs = State.folders[currdir]
            if do_refresh:
                subdirs.clear()
            if not subdirs:
                subdirs.extend(
                    airexec('return fs.find_dir_names(folder)', folder=currdir)
                )

            if new_folder_name:
                if new_folder_name in subdirs:
                    st.toast(
                        ':red[Failed to create new folder: duplicate name!]',
                        duration='long',
                    )
                    State.tree_select_index_1 = subdirs.index(new_folder_name)
                else:
                    airexec(
                        'fs.make_dir(path)',
                        path='{}/{}'.format(currdir, new_folder_name),
                    )
                    st.toast(':green[Folder created.]')
                    subdirs.append(new_folder_name)
                    subdirs.sort()
                    State.tree_select_index_1 = subdirs.index(new_folder_name)
                    State.temp_hold_dialog_opened = True
                    st.rerun()

            with st.container(height=300):
                target_dirname = st.radio(
                    'Select folder', subdirs, index=State.tree_select_index_1
                )
                result = (
                    target_dirname is None
                    and currdir
                    or '{}/{}'.format(currdir, target_dirname)
                )

            def change_dir(
                dirpath: str, relocate_subdir_name: str = ''
            ) -> None:
                if dirpath not in State.folders:
                    State.folders[dirpath] = airexec(
                        'return fs.find_dir_names(folder)', folder=dirpath
                    )
                State.tree_select_index_0 = sorted(State.folders).index(dirpath)
                if relocate_subdir_name:
                    State.tree_select_index_1 = State.folders[dirpath].index(
                        relocate_subdir_name
                    )
                else:
                    State.tree_select_index_1 = 0
                State.temp_hold_dialog_opened = True
                st.rerun()

            if do_back:
                a, b = currdir.rsplit('/', 1)
                change_dir(a, relocate_subdir_name=b)
            elif do_enter and result != currdir:
                change_dir(result)
            else:
                a, b = result.rsplit('/', 1)
                st.markdown('You selected: **{}/:blue[{}]**'.format(a, b))

    if do_confirm:
        from .depsland_installer_online import State as MainState

        MainState.installation_path = (
            result.endswith('/Depsland') and result or result + '/Depsland'
        )
        st.rerun()


def _init_remote_env():
    State.air_client.exec(
        """
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
        
        def extracting(file_7z, folder):
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
                file_7z,
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

        # def is_folder(path: str) -> bool:
        #     return fs.is_dir(path)
        
        return None
        """
    )


def _refresh_tree_model():
    parent_folders = airexec(
        """
        def list_folders():
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
                folders.append(d.replace('\\\\', '/'))
            
            folders.sort()
            return folders

        return list_folders()
        """
    )
    State.folders.clear()
    for i, f in enumerate(parent_folders):
        State.folders[f] = []
        if f.startswith('C:/') and f.endswith('/AppData'):
            State.tree_select_index_0 = i
