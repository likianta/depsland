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
        for name in os.listdir(dir_o):
            if name not in ('pypi', 'python'):
                if os.path.isdir(x := f'{dir_o}/{name}'):
                    fs.remove_tree(x)
                else:
                    os.remove(x)
        fs.remove_tree(f'{dir_o}/python/Lib/site-packages')
    
    print(f'copying dir from "{dir_i}" to "{dir_o}" '
          f'(this may take long time, please wait...)')
    for name in os.listdir(dir_i):
        if name not in ('pypi', 'python', 'setup.exe'):
            print(':i', name)
            fs.move(f'{dir_i}/{name}', f'{dir_o}/{name}')
    print('moving python site-packages...', ':i')
    if os.path.islink(f'{dir_i}/python'):  # TEST
        fs.copy_tree(f'{dir_i}/python/Lib/site-packages',
                     f'{dir_o}/python/Lib/site-packages')
    else:
        fs.move(f'{dir_i}/python/Lib/site-packages',
                f'{dir_o}/python/Lib/site-packages')
    
    # # create shortcut to desktop
    # file_i = f'{dir_o}/depsland.exe'
    # file_o = '{}/Desktop/depsland.lnk'.format(os.environ['USERPROFILE'])
    
    # add to environment variables
    if not os.getenv('DEPSLAND'):
        run_cmd_args('setx', 'DEPSLAND', dir_o.replace('/', '\\'))
    print('added `DEPSLAND` to environment variables')
    
    # if '%DEPSLAND%' not in os.environ['PATH']:
    #     print('add `%DEPSLAND%` to `%PATH%` variables')
    #     run_cmd_args('setx', 'PATH', '%PATH%;%DEPSLAND%')
    # print('added to PATH variables')
    
    print(':trf2', '[green]installation done[/]')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        from lk_logger.console import console
        console.print_exception()
    finally:
        input('press enter to close... ')
