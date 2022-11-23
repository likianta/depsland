"""
dependencies:
    - argsense
    - lk-logger
    - lk-utils
"""
import os
import typing as t
from os.path import exists
from textwrap import dedent

import lk_logger
from argsense import cli
from lk_logger.console import console
from lk_utils import dumps
from lk_utils import fs
from lk_utils import run_cmd_args

lk_logger.setup(quiet=True, show_source=False, show_funcname=False)

if os.name != 'nt':
    print('this script is only for Windows.')
    input('press ENTER to exit... ')
    exit(0)
else:
    import winreg


@cli.cmd()
def main(do_replace_site_packages=True):
    dir_i = fs.xpath('..', True)
    dir_o = _choose_target_dir()
    
    if not exists(dir_o):
        _first_time_setup(dir_i, dir_o)
    else:
        _incremental_setup(dir_i, dir_o, do_replace_site_packages)
    
    _wind_up(dir_o)
    
    print(':trf2', '[green]installation done[/]')


def _choose_target_dir() -> str:
    def find_if_last_version_exists() -> t.Optional[str]:
        return os.getenv('DEPSLAND', None)
    
    default = (
            find_if_last_version_exists()
            or fs.normpath(os.environ['LocalAppData'] + '/Depsland')
        #   why LocalAppData?
        #   - https://www.zhihu.com/question/546008367
        #   - https://stackoverflow.com/questions/22107812/privileges-owner-
        #     issue-when-writing-in-c-programdata
    )
    
    cmd = console.input(
        'please choose a location to install depsland. \n'
        '[dim](the deafult path is [magenta]{}[/])[/] \n'.format(default) +
        'press ENTER to use default path, or input a folder here: '
    ).strip()
    
    if cmd == '':
        return default
    else:
        out = fs.normpath(cmd)
        # make sure the user defined path should be empty or not exist.
        if exists(out):
            if os.listdir(out):
                raise FileExistsError(out)
            else:
                fs.remove_tree(out)
        return out


def _first_time_setup(dir_i: str, dir_o: str) -> None:
    print('this is the first time you setup depsland app.')
    os.mkdir(dir_o)
    
    print('copying files from "{}" to "{}"'.format(dir_i, dir_o))
    
    for name in os.listdir(dir_i):
        if name == 'setup.exe':
            continue
        
        print(':ir', f'[green]{name}[/]')
        
        if name == 'python':
            if os.path.islink(f'{dir_i}/{name}'):  # dev mode
                fs.make_link(f'{dir_i}/{name}', f'{dir_o}/{name}')
                continue
            else:
                print('this may take a long time, please wait...', ':vs')
        
        if os.path.isfile(f'{dir_i}/{name}'):
            fs.copy_file(f'{dir_i}/{name}', f'{dir_o}/{name}')
        else:
            fs.copy_tree(f'{dir_i}/{name}', f'{dir_o}/{name}')


def _incremental_setup(dir_i: str, dir_o: str,
                       do_replace_site_packages=True) -> None:
    dir_m = f'{dir_o}/backup'
    if not exists(dir_m):
        os.mkdir(dir_m)
    
    # remove old version
    print('detect existed old version, remove...')
    for name in os.listdir(dir_o):
        if name == 'backup':
            continue
        elif name == 'python' and do_replace_site_packages:
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
    for name in os.listdir(dir_i):
        # assert name != 'backup'
        if name == 'setup.exe':
            continue
        elif name == 'python':
            print(':ir', f'[green]{name}[/]')
            print('this may take long time, please wait...', ':vs')
            if do_replace_site_packages:
                fs.copy_tree(f'{dir_i}/python/Lib/site-packages',
                             f'{dir_o}/python/Lib/site-packages')
                fs.copy_tree(f'{dir_i}/python/Scripts',
                             f'{dir_o}/python/Scripts')
            else:
                if exists(x := f'{dir_i}/python/Lib/site-packages'):
                    for sub_name in os.listdir(x):
                        if os.path.isfile(f'{x}/{sub_name}'):
                            fs.copy_file(
                                f'{x}/{sub_name}',
                                f'{dir_o}/python/Lib/site-packages/{sub_name}',
                                True
                            )
                        else:
                            fs.copy_tree(
                                f'{x}/{sub_name}',
                                f'{dir_o}/python/Lib/site-packages/{sub_name}',
                                True,
                            )
        else:
            print(':ir', f'[green]{name}[/]')
            if os.path.isfile(f'{dir_i}/{name}'):
                fs.copy_file(f'{dir_i}/{name}', f'{dir_o}/{name}')
            else:
                fs.copy_tree(f'{dir_i}/{name}', f'{dir_o}/{name}')
    print(':i0s')
    
    # restore old assets
    print('restoring some old assets...')
    for name in ('apps', 'pypi'):
        print(':ir', f'[magenta]{name}[/]')
        fs.move(f'{dir_m}/{name}', f'{dir_o}/{name}', True)
    print(':i0s')
    
    # totally remove old version
    print('totally remove old version...')
    fs.remove_tree(dir_m)


def _wind_up(dir_: str) -> None:
    print('create executables')
    
    # to %DEPSLAND% root
    file_i = f'{dir_}/build/exe/depsland.exe'
    file_o = f'{dir_}/depsland.exe'
    fs.move(file_i, file_o, True)
    
    # to desktop
    file_i = f'{dir_}/desktop.exe'
    file_o = fs.normpath('{}/Desktop/Depsland.lnk'
                         .format(os.environ['USERPROFILE']))
    _create_desktop_shortcut(file_i, file_o)
    
    # -------------------------------------------------------------------------
    # add `DEPSLAND` to environment variables
    
    dir_ = dir_.replace('/', '\\')
    print(':v', dir_)
    
    def get_environment_variables() -> t.Tuple[str, str]:
        """
        get environment variables from Windows registry.
        
        q: why not use `os.environ`?
        a: `os.environ` may not update immediately if we are using a third
            party file explorer, like total commander, xyplorer, etc.
            ps: another way to resolve this is to restart the explorer.
        """
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 'Environment', 0,
            winreg.KEY_ALL_ACCESS
        )
        
        try:
            value, _ = winreg.QueryValueEx(key, 'DEPSLAND')
        except FileNotFoundError:
            value = ''
        env_depsland = value
        
        value, _ = winreg.QueryValueEx(key, 'PATH')
        env_path = value
        
        return env_depsland, env_path
    
    env_depsland, env_path = get_environment_variables()
    print(':v', env_depsland, env_path[:80] + '...')
    
    if env_depsland != dir_:
        print('add `DEPSLAND` to environment variables')
        run_cmd_args('setx', 'DEPSLAND', dir_)
    
    if dir_ not in env_path:
        env_path = env_path.split(';')
        
        # remove old version
        if env_depsland and env_depsland in env_path:
            env_path.remove(env_depsland)
            try:
                env_path.remove(env_depsland + r'\apps\.bin')
            except ValueError:
                pass
        
        print('add `DEPSLAND` to `PATH` (user variable)')
        # edit user environment variables through Windows registry
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 'Environment', 0,
            winreg.KEY_ALL_ACCESS
        )
        winreg.SetValueEx(
            key, 'PATH', 0, winreg.REG_EXPAND_SZ,
            ';'.join(filter(None, [dir_, dir_ + r'\apps\.bin'] + env_path))
        )
        winreg.CloseKey(key)


def _create_desktop_shortcut(file_i: str, file_o: str) -> None:
    """
    this function was copied from `depsland.utils.gen_exe.main.create_shortcut`.
    """
    vbs = fs.xpath('shortcut_gen.vbs')
    command = dedent('''
            Set objWS = WScript.CreateObject("WScript.Shell")
            lnkFile = "{file_o}"
            Set objLink = objWS.CreateShortcut(lnkFile)
            objLink.TargetPath = "{file_i}"
            objLink.Save
        ''').format(
        file_i=file_i.replace('/', '\\'),
        file_o=file_o.replace('/', '\\'),
    )
    dumps(command, vbs, ftype='plain')
    run_cmd_args('cscript', '/nologo', vbs)
    fs.remove_file(vbs)


if __name__ == '__main__':
    try:
        cli.run(main)
    except:
        console.print_exception()
    finally:
        print(':f2s')
        input('press enter to close... ')
