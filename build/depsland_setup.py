import os

from lk_utils import fs
from lk_utils import run_cmd_args


def main():
    assert os.name == 'nt', 'this script is only for Windows'
    
    dir_i = fs.xpath('../depsland', True)
    dir_o = fs.normpath(os.environ['ProgramData'] + '/Depsland')
    assert os.path.exists(dir_i)
    if os.path.exists(dir_o):
        fs.remove_tree(dir_o)
    
    fs.copy_tree(dir_i, dir_o)
    
    # # create shortcut to desktop
    # file_i = f'{dir_o}/depsland.exe'
    # file_o = '{}/Desktop/depsland.lnk'.format(os.environ['USERPROFILE'])
    
    # add to environment variables
    run_cmd_args('setx', 'DEPSLAND', dir_o.replace('/', '\\'))
    run_cmd_args('setx', 'PATH', '%PATH%;%DEPSLAND%')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        from lk_logger.console import console
        console.print_exception(e)
        input('press enter to exit...')
