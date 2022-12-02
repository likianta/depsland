if True:
    import sys
    from lk_utils import xpath
    sys.path.insert(0, xpath('../../lib'))

import os

from lk_utils import fs

from depsland import paths
from qmlease import QObject
from qmlease import app
from qmlease import pystyle
from qmlease import slot


class SetupWizard(QObject):
    
    @slot(result=str)
    def get_install_path(self) -> str:
        # if old version detected, return the old path.
        if x := os.getenv('DEPSLAND', None): return x
        # else use appdata/local as default.
        return fs.normpath(paths.system.local_app_data + '/Depsland')


pystyle.color.update_from_file(xpath('qml/stylesheet.yaml'))
app.register(SetupWizard(), 'setup_wizard')
app.run(xpath('qml/Main.qml'), debug=True)
