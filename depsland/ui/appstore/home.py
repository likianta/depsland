from lk_utils import xpath

from qmlease import QObject
from qmlease import app
from qmlease import bind_signal
from qmlease import slot


class Home(QObject):
    
    @slot(object, object, object)
    def init_view(self, input_: QObject, btn: QObject, msg: QObject) -> None:
        @bind_signal(btn.clicked)
        def _():
            from ...__main__ import install
            appid = input_['text']
            install(appid)


def launch_app() -> None:
    app.set_app_icon(xpath('../launcher.ico'))
    app.register(Home())
    app.run(xpath('qml/Home.qml'))
