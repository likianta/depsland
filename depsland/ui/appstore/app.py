import os.path
import typing as t
from time import sleep
from traceback import format_exception
from typing import cast

from lk_utils import new_thread
from lk_utils import xpath
from lk_utils.filesniff import filename
from lk_utils.subproc import ThreadWorker
from qmlease import AutoProp
from qmlease import QObject
from qmlease import app
from qmlease import bind_signal
from qmlease import pyassets
from qmlease import signal
from qmlease import slot


class T:
    AppToken = t.Optional[str]


def launch_app(default: T.AppToken = None, run_at_once: bool = False) -> None:
    """
    args:
        default: an appid or a path to a manifest file.
            if not given, the app will start normally.
        run_at_once: if true and default is set, will run app installation \
            immediately when UI is shown.
    """
    pyassets.set_root(xpath('qml/Assets'))
    app.set_app_icon(xpath('../launcher.ico'))
    app.register(Home(default, run_at_once))
    app.run(xpath('qml/Home.qml'))


class Home(QObject):
    running = cast(bool, AutoProp(False))
    _default: T.AppToken
    _info_item: QObject
    _info_updated = signal(str)  # this is for sub-thread to emit.
    _installation_done = signal(bool)
    _installing_thread: t.Optional[ThreadWorker] = None
    _startup_run: bool
    
    def __init__(self, app_token: T.AppToken = None, run_at_once: bool = False):
        super().__init__()
        self._default = app_token
        self._startup_run = run_at_once
    
    @slot(result=str)
    def get_app_version(self) -> str:
        from ... import __version__
        return f'v{__version__}'
    
    @slot(object, object, object, object, object)
    def init_view(
            self,
            input_bar: QObject,
            install_btn: QObject,
            stop_btn: QObject,
            info: QObject,
            drop_area: QObject,
    ) -> None:
        from ...config import auto_saved
        input_bar['text'] = (
            self._default or auto_saved['appstore']['last_input']
        )
        auto_saved.bind('appstore.last_input', lambda: input_bar['text'])
        app.on_exit_register(auto_saved.save)
        
        self._info_item = info
        self._info_item['text'] = _default_text = _gray(
            'Input an appid to install. '
            'For example: "hello_world".'
        )
        
        def bind_events():
            
            @bind_signal(input_bar.submit)
            def _(text: str) -> None:
                self._install(text)
            
            @bind_signal(install_btn.clicked)
            def _() -> None:
                self._install(input_bar['text'])
            
            @bind_signal(stop_btn.clicked)
            def _() -> None:
                if self._installing_thread.kill():
                    self._stop_timer()
                    self._transient_info(
                        _red('User force stopped.'),
                        _default_text
                    )
                else:
                    self._transient_info(
                        _red('Failed to stop the task! If you want to manually '
                             'stop it, please shutdown the window and restart '
                             'it.'),
                        duration=10
                    )
            
            @bind_signal(drop_area.fileDropped)
            def _(path: str) -> None:
                if path.endswith(('.pkl', '.yaml', '.yml', '.json')):
                    if filename(path, suffix=False) == 'manifest':
                        input_bar['text'] = path
            
            # -----------------------------------------------------------------
            
            @bind_signal(self.running_changed)
            def _(running: bool) -> None:
                install_btn['text'] = 'Install' if not running \
                    else 'Installing...'
                stop_btn['width'] = 100 if running else 0
            
            @bind_signal(self._info_updated)
            def _(text: str) -> None:
                self._info_item['text'] = text
            
            @bind_signal(self._installation_done)
            def _(success: bool) -> None:
                # self._installing_thread.join()
                self._stop_timer()
                if success:
                    self._transient_info(
                        _green('Installation done.'),
                        _default_text
                    )
                else:
                    self._transient_info(
                        _red('Installation failed. '
                             'See console output for details.'),
                        _default_text,
                        duration=5
                    )
        
        bind_events()
        
        if self._startup_run:
            self._install(self._default)
    
    def _install(self, app_token: T.AppToken) -> None:
        # check ability
        if self.running:
            self._transient_info(_yellow('Task is already running!'))
            return
        if not app_token:
            self._transient_info(_red('Appid cannot be empty!'))
            return
        
        if os.path.isabs(app_token):
            from ...manifest import load_manifest
            m = load_manifest(app_token)
            appid = m['appid']
            is_local = True
        else:
            appid = app_token
            is_local = False
        
        @new_thread()
        def install(text: str, is_local=False) -> None:
            if is_local:
                print('detected manifest file. use local install')
                from ...api.user_api import install_local as install
            else:
                from ...api.user_api import install_by_appid as install
            try:
                install(text)
                self._installation_done.emit(True)
            except Exception as e:
                print(''.join(format_exception(e)), ':v4')
                self._installation_done.emit(False)
        
        self._start_timer(appid)
        install(app_token, is_local)
    
    @new_thread()
    def _start_timer(self, appid: str) -> None:
        print(':t0s')  # reset timer
        time_sec = 0
        self.running = True
        while True:
            sleep(1)
            time_sec += 1
            if self.running:
                self._info_updated.emit(
                    f'Installing {appid}... (time elapsed: {time_sec}s)'
                )
            else:
                break
    
    def _stop_timer(self) -> None:
        self.running = False
    
    @new_thread()
    def _transient_info(
            self,
            text: str,
            restore: str = None,
            duration: float = 3.0
    ) -> None:
        """
        do not set text directly, because sub thread cannot do this. use signal
        to emit info change.
        """
        if restore is None:
            restore = self._info_item['text']
        self._info_updated.emit(text)
        sleep(duration)
        self._info_updated.emit(restore)


def _gray(text: str) -> str:
    return f'<font color="gray">{text}</font>'


def _red(text: str) -> str:
    return f'<font color="red">{text}</font>'


def _green(text: str) -> str:
    return f'<font color="green">{text}</font>'


def _yellow(text: str) -> str:
    return f'<font color="yellow">{text}</font>'
