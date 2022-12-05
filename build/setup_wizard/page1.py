import os

from lambda_ex import grafting
from lk_utils import fs

from build.setup_wizard.wizard import SetupWizard
from depsland import paths
from qmlease import QObject
from qmlease import signal
from qmlease import slot


class Page1(QObject):
    install_path_determined = signal(str)
    _input_item: QObject
    
    def __init__(self, wizard: SetupWizard):
        super().__init__()
        
        @grafting(wizard.navigation_ready.connect)
        def _():
            @grafting(wizard.nav.page_changed.connect)
            def _(page: int, direction: bool) -> None:
                if direction and page == 1:
                    self.install_path_determined.emit(self._input_item['text'])
    
    @slot(result=str)
    def get_install_path(self) -> str:
        # if old version detected, return the old path.
        if x := os.getenv('DEPSLAND', None): return x
        if os.name == 'nt':
            # else use appdata/local as default.
            return fs.normpath(paths.system.local_app_data + '/Depsland')
        else:
            print(':v3s', 'there is for testing only.')
            return fs.xpath('../../tests/programs/Depsland')
    
    @slot(object)
    def init_input_bar(self, input_bar: QObject) -> None:
        self._input_item = input_bar
