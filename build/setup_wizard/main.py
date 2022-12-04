from lk_utils import new_thread
if True:
    import PySide6  # noqa
    import sys
    from lk_utils import xpath
    sys.path.insert(0, xpath('../../lib'))

import os

from lambda_ex import grafting
from lk_utils import fs

from argsense import cli
from depsland import __version__ as depsland_version
from build.setup_wizard.page3 import Page3
from build.setup_wizard.page2 import Page2
from depsland import paths
from qmlease import AutoProp
from qmlease import Model
from qmlease import QObject
from qmlease import app
from qmlease import pystyle
from qmlease import signal
from qmlease import slot
from time import sleep


class SetupWizard(QObject):
    install_path_determined = signal(str)
    
    current_page = AutoProp(0, int)
    install_path = ''
    
    _prev_btn: QObject
    _next_btn: QObject
    
    # -------------------------------------------------------------------------
    
    @slot(object)
    def init_input_bar(self, input_bar: QObject) -> None:
        @grafting(input_bar.textChanged.connect)
        def _() -> None:
            print(input_bar['text'])
            self.install_path = input_bar['text']
    
    @slot(object, object)
    def init_nav_buttons(self, prev: QObject, next_: QObject) -> None:
        self._prev_btn = prev
        self._next_btn = next_
        
        @grafting(self._prev_btn.clicked.connect)
        def on_prev_clicked() -> None:
            self.current_page -= 1
        
        @grafting(self._next_btn.clicked.connect)
        def on_next_clicked() -> None:
            if self.current_page == 0:
                self.install_path_determined.emit(self.install_path)
            else:
                pass
            self.current_page += 1
        
        @grafting(self.current_page_changed.connect)
        def _(page: int) -> None:
            print(f'page changed to {page}')
            if page == 0:
                self._prev_btn['enabled'] = False
            else:
                self._prev_btn['enabled'] = True
            if page == 2:  # the last page
                self._next_btn['text'] = 'Finish'
            else:
                self._next_btn['text'] = 'Next'
    
    @slot(result=str)
    def get_install_path(self) -> str:
        # if old version detected, return the old path.
        if x := os.getenv('DEPSLAND', None): return x
        # else use appdata/local as default.
        return fs.normpath(paths.system.local_app_data + '/Depsland')


@cli.cmd()
def main(test_path=True, debug_mode=True):
    print(test_path, debug_mode)
    if test_path:
        dir_i = fs.xpath(f'../../dist/depsland-{depsland_version}', True)
        assert os.path.exists(dir_i)
        print(f'you are running test mode, the path is "{dir_i}"')
    else:
        dir_i = fs.xpath('../..', True)
    dir_o = ''
    
    wizard = SetupWizard()
    page2 = Page2(wizard, dir_i, dir_o)
    page3 = Page3(wizard)
    
    app.register(wizard, 'setup_wizard')
    app.register(page2, 'page2')
    app.register(page3, 'page3')
    
    pystyle.color.update_from_file(xpath('qml/stylesheet.yaml'))
    
    app.run(xpath('qml/Main.qml'), debug=debug_mode)


if __name__ == '__main__':
    cli.run(main)
