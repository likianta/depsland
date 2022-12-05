import os

from lambda_ex import grafting
from lk_utils import fs

from build.setup_wizard.wizard import SetupWizard
from depsland import paths
from qmlease import QObject
from qmlease import signal
from qmlease import slot
from qmlease import util


class Page1(QObject):
    path_determined = signal(str)
    
    browse_button: QObject
    input_bar: QObject
    
    def __init__(self, wizard: SetupWizard):
        super().__init__()
        
        @grafting(wizard.navigation_ready.connect)
        def _():
            @grafting(wizard.nav.page_changed.connect)
            def _(page: int, forward: bool) -> None:
                if forward and page == 1:
                    self.path_determined.emit(self.selected_path)
    
    @property
    def selected_path(self) -> str:
        return self.input_bar['text']
    
    @slot(object, object)
    def init_view(self, item1: QObject, item2: QObject) -> None:
        self.browse_button = item1
        self.input_bar = item2
        
        self.input_bar['text'] = self._get_default_installation_path()
        
        @grafting(self.browse_button.clicked.connect)
        def _():
            path = util.file_dialog(
                action='open',
                type_='folder',
                start_dir=self.selected_path
            )
            if path:
                self.input_bar['text'] = path
    
    @staticmethod
    def _get_default_installation_path() -> str:
        # if old version detected, return the old path.
        if x := os.getenv('DEPSLAND', None): return x
        if os.name == 'nt':
            # else use appdata/local as default.
            return fs.normpath(paths.system.local_app_data + '/Depsland')
        else:
            print(':v3s', 'there is for testing only.')
            return fs.xpath('../../tests/programs/Depsland')
