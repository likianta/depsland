"""
commands:
    test mode in early stage:
        py build/setup_wizard/main.py :true :true
    test mode in lately stage:
        py build/setup_wizard/main.py :true :false
    production release:
        py build/setup_wizard/main.py :false :false
"""
from argsense import cli


@cli.cmd()
def main(test_path: bool = False, hot_reload: bool = False) -> None:
    from depsland import __version__ as depsland_version
    from lk_utils import xpath
    from os.path import exists
    from qmlease import app
    from qmlease import pystyle
    from .page1 import Page1
    from .page2 import Page2
    from .page3 import Page3
    from .wizard import wizard
    
    if test_path:
        dir_i = xpath(f'../../dist/depsland-setup-{depsland_version}', True)
        assert exists(dir_i), dir_i
        print(f'you are running in test mode, the path is "{dir_i}"')
    else:
        dir_i = xpath('../../', True)
    dir_o = ''
    
    page1 = Page1()
    page2 = Page2(page1, dir_i, dir_o)
    page3 = Page3()
    
    app.register(wizard, 'setup_wizard')
    app.register(page1, 'page1')
    app.register(page2, 'page2')
    app.register(page3, 'page3')
    
    pystyle.color.update_from_file(xpath('stylesheet.yaml'))
    
    app.set_app_icon(xpath('launcher.ico'))
    app.run(xpath('qml/Main.qml'), debug=hot_reload)


if __name__ == '__main__':
    cli.run(main)
