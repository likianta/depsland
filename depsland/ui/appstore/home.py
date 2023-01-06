from time import sleep
from typing import cast

from lk_utils import new_thread
from lk_utils import xpath
from lk_utils.subproc import ThreadWorker

from qmlease import AutoProp
from qmlease import QObject
from qmlease import app
from qmlease import bind_signal
from qmlease import log
from qmlease import pyassets
from qmlease import slot


class Home(QObject):
    running = cast(bool, AutoProp(False))
    _installing: ThreadWorker
    _msg_item: QObject
    
    @slot(object, object, object)
    def init_view(self, input_: QObject, btn: QObject, msg: QObject) -> None:
        self._msg_item = msg
        
        @bind_signal(btn.clicked)
        def _() -> None:
            self.running = not self.running
        
        @bind_signal(self.running_changed)
        def _(running: bool) -> None:
            if running:
                btn['text'] = 'Installing...'
                appid = input_['text']
                log(appid)
                self._start_timer(appid)
                self._installing = self._install(appid)  # noqa
            else:
                btn['text'] = 'Install'
                self._stop_timer()
    
    @new_thread()
    def _install(self, appid: str) -> None:
        from ...__main__ import install
        install(appid)
    
    @new_thread()
    def _start_timer(self, appid: str) -> None:
        time_sec = 0
        while self.running:
            sleep(1)
            time_sec += 1
            self._msg_item['text'] = \
                f'Installing {appid}... (time elapsed: {time_sec}s)'
            if self._installing.
    
    def _stop_timer(self) -> None:
        self.running = False
        self._msg_item['text'] = ''


def launch_app() -> None:
    pyassets.set_root(xpath('qml/Assets'))
    app.set_app_icon(xpath('../launcher.ico'))
    app.register(Home())
    app.run(xpath('qml/Home.qml'))
    # app.run(xpath('qml/Home.qml'), debug=True)