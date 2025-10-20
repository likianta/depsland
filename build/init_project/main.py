import sys
from argsense import cli
from depsland.platform.launcher.make_exe import add_icon_to_exe
from lk_utils import fs
from lk_utils import run_cmd_args


@cli
def init_project_tree():
    # prerequisites
    
    if not fs.exist('chore/python_embed'):
        raise Exception(
            '''
            1. get python embedded version from ...
            2. extract it to "chore/python_embed"
            3. edit "chore/python_embed/python312._pth" to be like below:
                python312.zip
                .
                ..
                ../chore/site_packages
            4. re-run this script.
            '''
        )
    
    # -------------------------------------------------------------------------
    
    fs.make_link(
        '{}/Lib/site-packages'.format(fs.parent(sys.executable)), 'chore/.venv')
    fs.make_link('chore/python_embed', 'python')


@cli
def make_all_exe_files():
    def make(file, name, icon, show_console):
        # assert f.endswith('.v') and n.endswith('.exe')
        print(name, ':piv2')
        file_i = file
        file_o = 'build/exe/{}'.format(name)
        run_cmd_args('v', '-prod', '-o', file_o, file_i, verbose=True)
        add_icon_to_exe(file_o, icon)
    
    make(
        'build/init_project/depsland_app_maker.v',
        'Depsland AppMaker.exe',
        'build/icon/python.ico',
        True,
    )
    
    make(
        'build/init_project/depsland_app_store.v',
        'Depsland AppStore.exe',
        'build/icon/launcher.ico',
        False,
    )
    
    print(':t', 'done')


if __name__ == '__main__':
    # make sure vlang is installed and added to env:PATH
    # pox build/init_project/main.py -h
    cli.run()
