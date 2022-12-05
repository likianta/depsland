import os
from time import sleep

from lk_utils import fs
from lk_utils import new_thread

from build.setup_wizard.page1 import Page1
from qmlease import Model
from qmlease import QObject
from qmlease import signal
from qmlease import slot


class Page2(QObject):  # InProgress
    index_changed = signal(int)
    
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
        
        page1.install_path_determined.connect(self.confirm_dir_o)
    
    @slot(str)
    def confirm_dir_o(self, dir_o: str) -> None:
        print(':v2', 'target path is determined', dir_o)
        self._dir_o = dir_o
        self.run()
    
    @slot(result=object)
    def get_model(self) -> Model:
        return self._model
    
    # noinspection PyNoneFunctionAssignment
    @new_thread(singleton=True)
    def run(self) -> None:
        sleep(0.3)  # wait for the UI to be ready.
        
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
            name = item['name']
            print(':ir', f'[green]{name}[/]')
            if name == 'python':
                if os.path.islink(f'{self._dir_i}/{name}'):  # dev mode
                    subthread = updating(index, 100E-3)
                else:
                    self._model.update(index, {
                        'processing': f'Extracting {name}. '
                                      f'This may take a while, please wait...'
                    })
                    subthread = updating(index, 10)
            else:
                self._model.update(index, {'processing': f'Extracting {name}'})
                subthread = updating(index, 1)
            
            i, o = f'{self._dir_i}/{name}', f'{self._dir_o}/{name}'
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
