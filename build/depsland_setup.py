import os
from os.path import exists

import lk_logger
from lk_utils import fs
from lk_utils import run_cmd_args

lk_logger.setup(quiet=True, show_source=False, show_funcname=False)


def main():
    assert os.name == 'nt', 'this script is only for Windows'
    
    dir_i = fs.xpath('..', True)
    dir_o = fs.normpath(os.environ['ProgramData'] + '/Depsland')
    dir_m = f'{dir_o}/backup'
    
    # -------------------------------------------------------------------------
    
    assert exists(f'{dir_i}/depsland')
    if exists(dir_o):
        print('detect existed old version, remove...')
        if not exists(dir_m):
            os.mkdir(dir_m)
        for name in os.listdir(dir_o):
            if name == 'backup': continue
            print(':ir', f'[red dim]{name}[/]')
            fs.move(f'{dir_o}/{name}', f'{dir_m}/{name}', True)
        print(':i0s')
    else:
        os.mkdir(dir_o)
    
    # -------------------------------------------------------------------------
    
    print(f'copying files from "{dir_i}" to "{dir_o}"')
    print('this may take long time, please wait...', ':vs')
    
    for name in os.listdir(dir_i):
        # assert name != 'backup'
        if name == 'setup.exe':
            continue
        else:
            print(':ir', f'[green]{name}[/]')
            fs.move(f'{dir_i}/{name}', f'{dir_o}/{name}', True)
    print(':i0s')
    
    if exists(dir_m):
        print('restoring some old assets...')
        print(':ir', f'[magenta]pypi[/]')
        fs.move(f'{dir_m}/pypi', f'{dir_o}/pypi', True)
        print(':i0s')
        print('remove old version...')
        fs.remove_tree(dir_m)
    
    # -------------------------------------------------------------------------
    
    print('create executables')
    
    file_i = f'{dir_o}/build/exe/desktop.exe'
    file_o = fs.normpath('{}/Desktop/Depsland.exe'
                         .format(os.environ['USERPROFILE']))
    fs.copy_file(file_i, file_o, True)
    
    file_i = f'{dir_o}/build/exe/depsland.exe'
    file_o = f'{dir_o}/depsland.exe'
    fs.move(file_i, file_o, True)
    
    # -------------------------------------------------------------------------
    
    dir_o = dir_o.replace('/', '\\')
    if os.getenv('DEPSLAND', '') != dir_o:
        print('add `DEPSLAND` to environment variables')
        run_cmd_args('setx', 'DEPSLAND', dir_o)
    
    if dir_o not in os.environ['PATH']:
        print('add `DEPSLAND` to `PATH` (user variable)')
        # edit user environment variables through windows registry
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 'Environment', 0,
            winreg.KEY_ALL_ACCESS
        )
        value, _ = winreg.QueryValueEx(key, 'PATH')
        value = ';'.join((dir_o, f'{dir_o}/apps_launcher', value))
        winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)
    
    print(':trf2', '[green]installation done[/]')


if __name__ == '__main__':
    try:
        main()
    except:
        from lk_logger.console import console
        console.print_exception()
    finally:
        input('press enter to close... ')
