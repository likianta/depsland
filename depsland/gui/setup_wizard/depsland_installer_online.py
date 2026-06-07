if not __package__:
    __package__ = 'depsland.gui.setup_wizard'

import typing as tp
from contextlib import contextmanager

import streamlit as st
import streamlit_canary as sc
from argsense import cli

from . import advanced
from . import remote
from .remote import aircall
from .remote import airexec


@sc.init_state
class State:
    depsland_old_pypi_path = ''
    depsland_root = ''
    depsland_url = (
        'https://likianta-public-share.oss-cn-shanghai.aliyuncs.com'
        '/depsland-resources/depsland.7z'
    )
    depsland_version = '0.12.0a22'
    #   this field required manually update. make sure it matches
    #   `pyproject.toml:project.version`.
    depsland_zip = ''
    installation_done = False
    installation_path = ''
    target: tp.Optional[tp.Tuple[str, str]] = None
    __version__ = 32


@cli
def main(
    debug: bool = False,
    **kwargs,
    # client_public_host: tp.Optional[str] = None,
    # client_public_port: tp.Optional[int] = None,
    # target_appid: tp.Optional[str] = None,
    # target_version: tp.Optional[str] = None,
) -> None:
    st.set_page_config('Online Installing Depsland')
    st.title('Online Installing :red[Depsland]')

    if not remote.State.air_client:
        State.target = remote.init_air_client(debug, **kwargs)
        State.installation_path = aircall('get_default_installation_path')

    if not State.installation_done:
        _ask_folder()

    with st.container(horizontal=True):
        do_inst = st.button(
            'Install',
            type='primary',
            width=160,
            disabled=State.installation_done,
        )
        do_close_place = st.empty()
    above_progress_place = st.empty()
    if do_inst:
        with st.expander('Installation progress', True):
            depsland_direct_path = _install_depsland(State.installation_path)
            if State.target:
                _install_target_application(depsland_direct_path, *State.target)
            State.installation_done = True
            # remote.close_air_client()
    if State.installation_done:
        with above_progress_place:
            st.success(
                """
                Successfully installed {}! 🎉🎉🎉
                
                You can now close this window and **rerun** the same ".exe" file 
                to launch target application.
                """.format(
                    State.target
                    and 'Depsland and the target application'
                    or 'Depsland'
                )
            )
        with do_close_place:
            st.button(':red[Close this window/tab]', on_click=_close_tab_2)

    if debug:
        with sc.row('center'):
            if st.button('Refresh remote environment'):
                remote._init_remote_env()
            if st.button('Test'):
                st.markdown(':green[{}]'.format(aircall('test', 'Alice')))
            # if st.button(':red[Force close]'):
            #     remote.close_air_client()
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
                    """
                    If input an empty folder or a non-existent folder path, will 
                    use it as installation path.

                    If input a non-empty folder path, will use 
                    `<the_given_path>/Depsland` as installation path.
                    """
                ),
            )
            if path:
                path = path.replace('\\', '/')
                # assert aircall('is_dir', path)
                if aircall('is_empty_folder', path):
                    State.installation_path = path
                else:
                    path += '/Depsland'
                    if aircall('is_empty_folder', path):
                        with place2:
                            st.warning(
                                'Please select an **empty** folder or an '
                                '**inexisting** folder to install.'
                            )
                    else:
                        State.installation_path = path
                print(State.installation_path)

            if (
                st.button('Browse', width=120)
                or remote.State.temp_hold_dialog_opened
            ):
                # popup st-dialog and show tree view.
                remote.State.temp_hold_dialog_opened = False
                remote.tree_view()

            with st.popover('Advanced options'):
                State.depsland_zip, State.depsland_old_pypi_path = (
                    advanced.main()
                )


def _close_tab_1() -> None:
    # FIXME: doesn't work.
    st.html('<script>window.close();</script>', unsafe_allow_javascript=True)
    remote.close_air_client()


def _close_tab_2() -> None:
    # simulate `ctrl + w` in client side using only standard python libraries.
    airexec(
        """
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
        """
    )
    remote.close_air_client()


def _install_depsland(root: str) -> str:
    place1 = st.empty()
    label1 = ':one: Downloading Depsland.7z from internet...'
    prog1 = st.progress(0)
    place2 = st.empty()
    label2 = ':two: Unpacking resources...'
    prog2 = st.progress(0)

    with place1:
        st.markdown(label1 + ' :gray[wait]')
    with place2:
        st.markdown(label2 + ' :gray[wait]')

    if State.depsland_zip:
        print('skip downloading depsland.7z because we use cached file.')
    version = State.depsland_version
    path0 = root  # parent folder
    path1 = root + '/depsland-' + version + '.7z'  # zip file
    path2 = root + '/' + version  # extracted folder
    airexec(
        """
        if not fs.exist(root):
            fs.make_dirs(root)
        """,
        root=path0,
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
        if State.depsland_zip:
            prog.progress(1.0, 'Depsland already downloaded.')
        else:
            # for x in aircall('downloading', State.depsland_url, path1):
            #     np.show(x, ':vni1')
            #     p, t = x
            #     prog.progress(p, t)
            for p, t in aircall('downloading', State.depsland_url, path1):
                # print(p, t, ':iv')
                prog.progress(p, t)

    with notify_extracting_status() as prog:
        for p, t in aircall('extracting', path1, path2):
            # print(p, t, ':iv')
            prog.progress(p, t)
    if State.depsland_old_pypi_path:
        airexec(
            """
            fs.move(pypi_src, pypi_dst, True)
            fs.make_link(pypi_dst, pypi_src, False)
            """,
            pypi_src=State.depsland_old_pypi_path,
            pypi_dst=path2 + '/pypi',
        )

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

    generator = airexec(
        """
        def run_depsland_install(depsland_root, appid, version):
            if sys.path[0] != depsland_root:
                sys.path.insert(0, depsland_root)
                sys.path.insert(1, depsland_root + '/chore/minideps')
            
            if 'depsland' in sys.modules:
                sys.modules.pop('depsland')
            import depsland
            print(depsland.__path__)
            
            from depsland.api.user_api import install_by_appid
            from depsland.api.user_api import install_progress
            
            progress = ('', 0.0, '')  # Tuple[Stage, Percent, Text]
            progress_done = False
            
            @install_progress.bind
            def _update_progress(stage, percent, text):
                nonlocal progress, progress_done
                if stage == 'updating_assets':
                    progress = (stage, percent, text)
                elif stage == 'resolving_dependencies':
                    progress = (stage, percent, text)
                elif stage == 'linking_dependencies':
                    progress = ('ending', 0.0 + 0.7 * percent, text)
                elif stage == 'ending':
                    progress = ('ending', 0.7 + 0.3 * percent, text)
                    progress_done = percent >= 1.0
                else:
                    raise ValueError(stage)
            
            run_new_thread(install_by_appid, appid, version)
            
            while not progress_done:
                yield progress
                sleep(0.1)
            yield (progress[0], 1.0, progress[2])
        
        return run_depsland_install(depsland_root, appid, version)
        """,
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
            else:  # 'ending'
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


if __name__ == '__main__':
    # see `./readme.mo : Demo Run : Start GUI with debug arguments`
    cli.run(main)
