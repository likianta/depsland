if __name__ == '__main__':
    __package__ = 'depsland.gui.app_builder'

import qmlease as q
from lk_utils import fs
from .stylemanager import StyleManager

class Main(q.QObject):
    pass

q.app.register(Main())
q.app.register(StyleManager(), 'StyleManager', namespace='global')
q.app.run(fs.xpath('qml/Main.qml'))
