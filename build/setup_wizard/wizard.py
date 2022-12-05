from lambda_ex import grafting

from qmlease import QObject
from qmlease import app
from qmlease import signal
from qmlease import slot


class SetupWizard(QObject):
    nav: 'Navigation'
    navigation_ready = signal()
    
    @slot(object, object)
    def init_navigation(self, prev: QObject, next_: QObject) -> None:
        self.nav = Navigation(prev, next_)
        self.navigation_ready.emit()


class Navigation(QObject):
    FIRST_PAGE = 0
    LAST_PAGE = 2
    # current_page = AutoProp(0, int)
    current_page = int
    page_changed = signal(int, bool)
    #   bool: True means forward, False means backward.
    prev_btn: QObject
    next_btn: QObject
    
    def __init__(self, prev_btn: QObject, next_btn: QObject):
        super().__init__()
        self.prev_btn = prev_btn
        self.next_btn = next_btn
        self._init_bindings()
    
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
            if self.current_page == self.LAST_PAGE:
                app.exit()
            else:
                self.current_page += 1
                self.page_changed.emit(self.current_page, True)
        
        @grafting(self.page_changed.connect)
        def _(page: int, __) -> None:
            print(f'page changed to {page}')
            if page == self.FIRST_PAGE:
                self.prev_btn['enabled'] = False
            else:
                self.prev_btn['enabled'] = True
            if page == self.LAST_PAGE:
                self.next_btn['text'] = 'Finish'
            else:
                self.next_btn['text'] = 'Next'
