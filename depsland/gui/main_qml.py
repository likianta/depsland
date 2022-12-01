if True:
    import sys
    from lk_utils import xpath
    sys.path.insert(0, xpath('../../lib'))

from qmlease import app
from qmlease import pystyle
pystyle.color.update_from_file(xpath('qml/stylesheet.yaml'))
app.run(xpath('qml/Main.qml'), debug=True)
