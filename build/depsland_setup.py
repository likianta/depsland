import os

import lk_logger
from lk_utils import fs
from lk_utils import run_cmd_args


lk_logger.setup(quiet=True, show_source=False, show_funcname=False)


def main():
    assert os.name == 'nt', 'this script is only for Windows'
    
    dir_i = fs.xpath('..', True)
    dir_o = fs.normpath(os.environ['ProgramData'] + '/Depsland')
    assert os.path.exists(f'{dir_i}/depsland')
    if os.path.exists(dir_o):
        print('detect existed old version, remove...')
        fs.remove_tree(dir_o)
    
    print(f'copy dir from "{dir_i}" to "{dir_o}" '
          f'(this may take several minutes...)')
    fs.copy_tree(dir_i, dir_o)
    
    # # create shortcut to desktop
    # file_i = f'{dir_o}/depsland.exe'
    # file_o = '{}/Desktop/depsland.lnk'.format(os.environ['USERPROFILE'])
    
    # add to environment variables
    if not os.getenv('DEPSLAND'):
        print('add `DEPSLAND` to environment variables')
        run_cmd_args('setx', 'DEPSLAND', dir_o.replace('/', '\\'))
    print('added to DEPSLAND variables')
    
    if '%DEPSLAND%' not in os.environ['PATH']:
        print('add `%DEPSLAND%` to `%PATH%` variables')
        run_cmd_args('setx', 'PATH', '%PATH%;%DEPSLAND%')
    print('added to PATH variables')
    
    print(':tr', '[green]installation done[/]')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        from lk_logger.console import console
        console.print_exception(e)
        input('press enter to exit... ')
    else:
        input('press enter to leave... ')
