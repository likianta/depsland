if True:
    import PySide6  # noqa
    import os
    import sys
    from lk_utils import xpath
    assert os.path.exists(xpath('../../lib/qmlease'))
    sys.path.insert(0, xpath('../../lib'))

from argsense import cli
from lk_utils import fs

from build.setup_wizard.page1 import Page1
from build.setup_wizard.page2 import Page2
from build.setup_wizard.page3 import Page3
from build.setup_wizard.wizard import SetupWizard
from depsland import __version__ as depsland_version
from qmlease import app
from qmlease import pystyle


@cli.cmd()
def main(test_path=True, debug_mode=True):
    print(test_path, debug_mode)
    if test_path:
        dir_i = fs.xpath(f'../../dist/depsland-{depsland_version}', True)
        assert os.path.exists(dir_i)
        print(f'you are running test mode, the path is "{dir_i}"')
    else:
        dir_i = fs.xpath('../..', True)
    dir_o = ''
    
    wizard = SetupWizard()
    page1 = Page1(wizard)
    page2 = Page2(page1, dir_i, dir_o)
    page3 = Page3(wizard)
    
    app.register(wizard, 'setup_wizard')
    app.register(page1, 'page1')
    app.register(page2, 'page2')
    app.register(page3, 'page3')
    
    pystyle.color.update_from_file(xpath('qml/stylesheet.yaml'))
    
    app.run(xpath('qml/Main.qml'), debug=debug_mode)


if __name__ == '__main__':
    cli.run(main)
