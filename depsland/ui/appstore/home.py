from time import sleep
from typing import cast

from lk_utils import new_thread
from lk_utils import xpath

from qmlease import AutoProp
from qmlease import QObject
from qmlease import app
from qmlease import bind_signal
# from qmlease import log
from qmlease import pyassets
from qmlease import slot


class Home(QObject):
    running = cast(bool, AutoProp(False))
    # _installing: ThreadWorker
    
    _btn_item: QObject
    _inp_item: QObject
    _msg_item: QObject
    
    @slot(object, object, object)
    def init_view(self, input_: QObject, btn: QObject, msg: QObject) -> None:
        self._btn_item = btn
        self._inp_item = input_
        self._msg_item = msg
        
        @bind_signal(btn.clicked)
        def _() -> None:
            self.running = not self.running
        
        @bind_signal(self.running_changed)
        def _(running: bool) -> None:
            if running:
                btn['text'] = 'Installing...'
                appid = input_['text']
                print(':v2', appid)
                self._start_timer(appid)
                self._install(appid)
                self._transient_text('Done', 'Install')
                self.running = False
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
            pass
    
    def _stop_timer(self) -> None:
        self.running = False
        self._msg_item['text'] = ''
    
    @new_thread()
    def _transient_text(self, before: str, after: str) -> None:
        self._btn_item['text'] = before
        sleep(1)
        self._btn_item['text'] = after


def launch_app() -> None:
    pyassets.set_root(xpath('qml/Assets'))
    app.set_app_icon(xpath('../launcher.ico'))
    app.register(Home())
    app.run(xpath('qml/Home.qml'))
    # app.run(xpath('qml/Home.qml'), debug=True)
