import typing as t

from lambda_ex import grafting

from qmlease import AutoProp
from qmlease import QObject
from qmlease import app
from qmlease import signal
from qmlease import slot


class SetupWizard(QObject):
    all_finished = AutoProp(False, bool)
    nav: 'Navigation'
    navigation_ready = signal()
    page_changed = signal(int)
    
    @slot(object, object)
    def init_navigation(self, prev: QObject, next_: QObject) -> None:
        self.nav = Navigation(prev, next_)
        
        @grafting(self.nav.page_changed.connect)
        def _(page: int, _: bool) -> None:
            self.page_changed.emit(page)
        
        self.navigation_ready.emit()


class Navigation(QObject):
    FIRST_PAGE = 0
    LAST_PAGE = 2
    # current_page = AutoProp(0, int)
    current_page = 0
    page_changed = signal(int, bool)
    #   bool: True means forward, False means backward.
    prev_btn: QObject
    next_btn: QObject
    _steps_checker: t.List[t.Optional[t.Callable[[], bool]]]
    
    def __init__(self, prev_btn: QObject, next_btn: QObject):
        super().__init__()
        self.prev_btn = prev_btn
        self.next_btn = next_btn
        self._steps_checker = [None] * (self.LAST_PAGE + 1)
        self._init_bindings()
    
    def add_step_checker(self, step: int, checker: t.Callable) -> None:
        """
        the step checker is only triggered when user clicks 'Next' button.
        """
        self._steps_checker[step] = checker
    
    def _init_bindings(self):
        
        @grafting(self.prev_btn.clicked.connect)
        def _() -> None:
            if self.current_page == self.FIRST_PAGE:
                # this case should not happen, did we forget to disable the
                #   button in the qml UI?
                raise Exception()
            self.current_page -= 1
            self.page_changed.emit(self.current_page, False)
        
        @grafting(self.next_btn.clicked.connect)
        def _() -> None:
            if checker := self._steps_checker[self.current_page]:
                if not checker():
                    return
            
            if self.current_page == self.LAST_PAGE:
                app.exit()
            else:
                self.current_page += 1
                self.page_changed.emit(self.current_page, True)
        
        @grafting(self.page_changed.connect)
        def _(page: int, _) -> None:
            print(f'page changed to {page}')
            if page == self.FIRST_PAGE:
                self.prev_btn['enabled'] = False
            else:
                self.prev_btn['enabled'] = True
            if page == self.LAST_PAGE:
                self.next_btn['text'] = 'Finish'
            else:
                self.next_btn['text'] = 'Next'


wizard = SetupWizard()
