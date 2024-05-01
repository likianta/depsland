import os
from time import sleep
from typing import cast

from lk_utils import fs
from lk_utils import new_thread
from lk_utils import run_new_thread

from qmlease import AutoProp
from qmlease import Model
from qmlease import QObject
from qmlease import bind_signal
from qmlease import signal
from qmlease import slot
from .page1 import Page1
from .wizard import wizard


class Page2(QObject):  # InProgress
    index_changed = signal(int)
    # inprogressing = signal(bool)  # True: start; False: done
    inprogressing = cast(bool, AutoProp(False))
    
    def __init__(self, page1: Page1, dir_i: str, dir_o: str):
        super().__init__()
        
        self._dir_i = dir_i
        self._dir_o = dir_o
        self._model = Model(('name', 'progress', 'processing'))
        #   `processing` means 'processing information'.
        self._model.append_many([
            {'name': x, 'progress': 0, 'processing': ''}
            for x in os.listdir(dir_i) if x != 'setup.exe'
        ])
        
        page1.path_determined.connect(self._confirm_target)
        
        @bind_signal(self.inprogressing_changed)
        def _(running: bool) -> None:
            page1_status = not running
            wizard.nav.next_btn['enabled'] = page1_status
            page1.browse_button['enabled'] = page1_status
            page1.input_bar['enabled'] = page1_status
        
        @bind_signal(wizard.page_changed)
        def _(page: int) -> None:
            if page == 0:
                wizard.nav.next_btn['enabled'] = True
            elif page == 1:
                wizard.nav.next_btn['enabled'] = not self.inprogressing
    
    @slot(str)
    def _confirm_target(self, dir_o: str) -> None:
        if wizard.all_finished:
            return
        print(':v2', 'target path is determined', dir_o)
        self._dir_o = dir_o
        self.run()
    
    @slot(result=object)
    def get_model(self) -> Model:
        return self._model
    
    # noinspection PyNoneFunctionAssignment
    @new_thread(singleton=True)
    def run(self) -> None:
        self.inprogressing = True
        sleep(0.3)  # wait for the UI to be ready.
        print(':i0s', 'start progressing')
        
        is_done = False
        subthread = None
        
        @new_thread(singleton=True)
        def updating(index: int, eta: float) -> None:  # unit: s
            interval = round(eta / 99, 3)
            for i in range(99):
                if is_done: break
                self._model.update(index, {'progress': i})
                sleep(interval)
            else:
                self._model.update(index, {'progress': 99})
        
        def done(index) -> None:
            nonlocal is_done
            is_done = True
            subthread.join()  # type: ignore
            self._model.update(index, {
                'progress'  : 100,
                'processing': 'Done'
            })
            is_done = False  # reset
        
        for index, item in enumerate(self._model):
            self.index_changed.emit(index)
            name = item['name']  # noqa
            print(':ir', f'[green]{name}[/]')
            
            if name == 'python':
                if os.path.islink(f'{self._dir_i}/{name}'):
                    pass  # dev mode
                else:
                    self._model.update(index, {
                        'processing':
                            f'Extracting {name}. '
                            f'This may take a while, please wait...'
                    })
            else:
                self._model.update(index, {'processing': f'Extracting {name}'})
            
            i, o = f'{self._dir_i}/{name}', f'{self._dir_o}/{name}'
            subthread = updating(index, self._estimate_copying_time(i))
            
            if os.path.islink(i):
                fs.make_link(i, o)
            elif os.path.isfile(i):
                fs.copy_file(i, o)
            else:
                fs.copy_tree(i, o)
            done(index)
            sleep(30E-3)  # in-purpose delay to ease user's eyes. if it too
            #   fast, the UI (especially the animation of progress) doesn't
            #   look well.
            #   see also `qml/Page2.qml : LKCircleProgress :
            #   animateValueDuration`.
        
        print(':ti0', 'all done')
        self.inprogressing = False
        wizard.all_finished = True
        wizard.active_stage += 1
        run_new_thread(wizard.wind_up, args=(self._dir_o,), daemon=False)
    
    @staticmethod
    def _estimate_copying_time(path: str) -> float:
        """
        returns time in second.
        note: this is a very rough calculation. mostly based on experience.
        """
        if os.path.islink(path):
            return 200E-3
        elif os.path.isfile(path):
            return 1
        else:
            medium_dirs = ('lib',)
            large_dirs = ('python',)
            dirname = fs.basename(path)
            if dirname in medium_dirs:
                return 10
            elif dirname in large_dirs:
                return 60
            else:
                return 1
