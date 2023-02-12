import os

from lk_utils import fs

from build.setup_wizard.wizard import wizard
from depsland import paths
from qmlease import QObject
from qmlease import pystyle
from qmlease import bind_signal
from qmlease import signal
from qmlease import slot
from qmlease import util


class Page1(QObject):
    path_determined = signal(str)
    
    browse_button: QObject
    input_bar: QObject
    prompt: QObject
    
    def __init__(self):
        super().__init__()
        
        @bind_signal(wizard.navigation_ready)
        def _():
            wizard.nav.add_step_checker(0, self.validate_path)
            
            @bind_signal(wizard.nav.page_changed)
            def _(page: int, forward: bool) -> None:
                if wizard.active_stage == 0:
                    if forward and page == 1:
                        self.path_determined.emit(self.selected_path)
                        wizard.active_stage += 1
                        wizard.nav.remove_step_checker(0)
    
    @property
    def selected_path(self) -> str:
        return fs.normpath(self.input_bar['text'], True)
    
    @slot(object, object, object)
    def init_view(self, item1: QObject, item2: QObject, item3: QObject) -> None:
        self.browse_button = item1
        self.input_bar = item2
        self.prompt = item3
        
        self.input_bar['text'] = self._get_default_installation_path()
        
        @bind_signal(self.browse_button.clicked)
        def _():
            if self.selected_path:
                try:
                    parent_path = fs.parent_path(self.selected_path)
                except:
                    parent_path = ''
            else:
                parent_path = ''
            path = util.file_dialog(
                action='open',
                type_='folder',
                start_dir=parent_path
            )
            if path:
                self.input_bar['text'] = path
        
        @bind_signal(self.input_bar.textChanged)
        def _() -> None:
            self.prompt['text'] = ''
        
        @bind_signal(wizard.all_finished_changed)
        def _(is_done: bool) -> None:
            # assert is_done
            print(is_done, ':v')
            self.input_bar['enabled'] = False
            self.browse_button['enabled'] = False
            self.prompt['color'] = pystyle.color['text_success']
            self.prompt['text'] = 'The task is over. You can view the ' \
                                  'installation path in explorer then.'
    
    def validate_path(self) -> bool:
        if wizard.all_finished:
            return True
        if os.path.exists(self.selected_path):
            if os.path.isfile(self.selected_path):
                self.prompt['color'] = pystyle.color['text_danger']
                self.prompt['text'] = \
                    'File cannot be used as installation path.'
                return False
            if os.listdir(self.selected_path):
                self.prompt['color'] = pystyle.color['text_danger']
                self.prompt['text'] = 'The path is not empty.'
                return False
        else:
            os.mkdir(self.selected_path)
        return True
    
    @staticmethod
    def _get_default_installation_path() -> str:
        # if old version detected, return the old path.
        if x := os.getenv('DEPSLAND', None):
            print(':v', 'old version detected', x)
            return x
        if os.name == 'nt':
            # else use appdata/local as default.
            return fs.normpath(paths.system.local_app_data + '/Depsland')
        else:
            print(':v3s', 'there is for testing only.')
            return fs.xpath('../../tests/programs/Depsland')
