import os
from os.path import exists

import lk_logger
from lk_logger.console import console
from lk_utils import fs
from lk_utils import run_cmd_args

lk_logger.setup(quiet=True, show_source=False, show_funcname=False)


def main():
    assert os.name == 'nt', 'this script is only for Windows'
    
    dir_i = fs.xpath('..', True)
    dir_o = _choose_target_dir()
    
    if not exists(dir_o):
        _first_time_setup(dir_i, dir_o)
    else:
        _incremental_setup(dir_i, dir_o)
    
    _wind_up(dir_o)
    
    print(':trf2', '[green]installation done[/]')
    

def _choose_target_dir() -> str:
    default = fs.normpath(os.environ['ProgramData'] + '/Depsland')
    cmd = console.input(
        'please choose a location to install depsland. \n'
        '[dim](the deafult path is [magenta{}[/])[/] \n'.format(default) +
        'press ENTER to use default path, or input a empty folder here: '
    ).strip()
    if cmd == '':
        return default
    else:
        out = cmd
        if not exists(out):
            os.mkdir(out)
        else:
            assert os.path.isdir(out) and len(os.listdir(out)) == 0, (
                'target directory should be empty!', out
            )
        return out


def _first_time_setup(dir_i: str, dir_o: str) -> None:
    print('this is the first time you setup depsland app.')
    os.mkdir(dir_o)
    
    print('copying files from "{}" to "{}"'.format(dir_i, dir_o))
    print('this may take long time, please wait...', ':vs')
    
    for name in os.listdir(dir_i):
        if name == 'setup.exe':
            continue
        print(':ir', f'[green]{name}[/]')
        if os.path.isfile(f'{dir_i}/{name}'):
            fs.copy_file(f'{dir_i}/{name}', f'{dir_o}/{name}')
        else:
            fs.copy_tree(f'{dir_i}/{name}', f'{dir_o}/{name}')


def _incremental_setup(dir_i: str, dir_o: str) -> None:
    dir_m = f'{dir_o}/backup'
    if not exists(dir_m):
        os.mkdir(dir_m)
    
    # remove old version
    print('detect existed old version, remove...')
    for name in os.listdir(dir_o):
        if name == 'backup':
            continue
        elif name == 'python':
            print(':ir', f'[red dim]{name}[/]')
            fs.move(f'{dir_o}/python/Lib/site-packages',
                    f'{dir_m}/python-lib-site_packages', True)
            fs.move(f'{dir_o}/python/Scripts',
                    f'{dir_m}/python-scripts', True)
        else:
            print(':ir', f'[red dim]{name}[/]')
            fs.move(f'{dir_o}/{name}', f'{dir_m}/{name}', True)
    print(':i0s')
    
    # copy new version
    print('copying files from "{}" to "{}"'.format(dir_i, dir_o))
    print('this may take long time, please wait...', ':vs')
    for name in os.listdir(dir_i):
        # assert name != 'backup'
        if name == 'setup.exe':
            continue
        elif name == 'python':
            print(':ir', f'[green]{name}[/]')
            fs.copy_tree(f'{dir_i}/python/Lib/site-packages',
                         f'{dir_o}/python/Lib/site-packages')
            fs.copy_tree(f'{dir_i}/python/Scripts',
                         f'{dir_o}/python/Scripts')
        else:
            print(':ir', f'[green]{name}[/]')
            if os.path.isfile(f'{dir_i}/{name}'):
                fs.copy_file(f'{dir_i}/{name}', f'{dir_o}/{name}')
            else:
                fs.copy_tree(f'{dir_i}/{name}', f'{dir_o}/{name}')
    print(':i0s')
    
    # restore old assets
    print('restoring some old assets...')
    for name in ('apps', 'apps_launcher', 'pypi'):
        print(':ir', f'[magenta]{name}[/]')
        fs.move(f'{dir_m}/{name}', f'{dir_o}/{name}', True)
    print(':i0s')
    
    # totally remove old version
    print('totally remove old version...')
    fs.remove_tree(dir_m)


def _wind_up(dir_: str):
    print('create executables')
    
    file_i = f'{dir_}/build/exe/desktop.exe'
    file_o = fs.normpath('{}/Desktop/Depsland.exe'
                         .format(os.environ['USERPROFILE']))
    fs.copy_file(file_i, file_o, True)
    
    file_i = f'{dir_}/build/exe/depsland.exe'
    file_o = f'{dir_}/depsland.exe'
    fs.move(file_i, file_o, True)
    
    # -------------------------------------------------------------------------
    # add `DEPSLAND` to environment variables
    
    dir_ = dir_.replace('/', '\\')
    if os.getenv('DEPSLAND', '') != dir_:
        print('add `DEPSLAND` to environment variables')
        run_cmd_args('setx', 'DEPSLAND', dir_)
    
    if dir_ not in os.environ['PATH']:
        print('add `DEPSLAND` to `PATH` (user variable)')
        # edit user environment variables through Windows registry
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 'Environment', 0,
            winreg.KEY_ALL_ACCESS
        )
        value, _ = winreg.QueryValueEx(key, 'PATH')
        value = ';'.join((dir_, f'{dir_}\\apps_launcher', value))
        #   FIXME: if old DEPSLAND is registered to PATH, remove it.
        winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, value)
        winreg.CloseKey(key)


if __name__ == '__main__':
    try:
        main()
    except:
        console.print_exception()
    finally:
        input('press enter to close... ')
