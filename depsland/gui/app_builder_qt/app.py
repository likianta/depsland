if __name__ == '__main__':
    __package__ = 'depsland.gui.app_builder_qt'

import qmlease as q
from lk_utils import fs

class Main(q.QObject):
    @q.Slot(object)
    def init_ui(self, root):
        @q.bind_signal(root.projectPathSubmit)
        def _load_project(path):
            assert fs.isdir(path)
            root['appName'] = fs.basename(path)
            root['appVersion'] = '0.1.0'

q.app.register(Main())
q.app.run(fs.xpath('qml/Main.qml'))
