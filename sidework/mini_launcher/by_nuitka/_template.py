import os
import re
import sys
import subprocess
import typing as t

# print(
#     __file__,
#     os.getpid(),
#     os.getppid(),
#     sys.argv,
#     sys.orig_argv,
#     sys.stdin,
#     sys.stdin.isatty(),
# )


def main(
    appid: str = '<APPID>',
    version: str = '<VERSION>',
    show_console: bool = '<SHOW_CONSOLE>',
) -> None:
    if root := _find_depsland_root():
        if _check_depsland_version(root):
            if appid == '<FROM_FILENAME>':
                # note: sys.argv = [<current_exe_file>]
                # print(__file__, sys.argv)
                # 'hello_world-v0.1.0.exe' -> 'hello_world'
                # 'hello_world-v0.1.0-common.exe' -> 'hello_world'
                # 'hello_world-v0.1.0-common (2).exe' -> 'hello_world'
                # 'hello_world-v0.1.0-debug.exe' -> 'hello_world'
                appid = os.path.basename(sys.argv[0]).split('-')[0]
            if version == '<FROM_FILENAME>':
                # 'hello_world-v0.1.0.exe' -> '0.1.0'
                # 'hello_world-v0.1.0-common.exe' -> '0.1.0'
                # 'hello_world-v0.1.0-debug.exe' -> '0.1.0'
                x = os.path.basename(sys.argv[0]).split('-')[1]
                assert x.startswith('v')
                if x.endswith('.exe'):
                    version = x[1:-4]
                else:
                    version = x[1:]
            _run_app(root, appid, version, show_console)
    else:
        raise NotImplementedError


def _find_depsland_root() -> t.Optional[str]:
    # (A)
    if x := os.getenv('DEPSLAND'):
        if os.path.exists('{}/apps/.bin/depsland.exe'.format(x)):
            return x
    # (B)
    #   consider that the A method may fail because current session didn't -
    #   update itself to sync with system environment settings, so we read the -
    #   registry key directly to get the latest env variable.
    if os.name == 'nt':
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            'Environment',
            0,
            winreg.KEY_READ
        )
        try:
            value, _ = winreg.QueryValueEx(key, 'DEPSLAND')
        except FileNotFoundError:
            value = None
        finally:
            winreg.CloseKey(key)
        if value and os.path.exists(
            '{}/apps/.bin/depsland.exe'.format(value)
        ):
            return value
    return None


def _check_depsland_version(depsland_root: str) -> bool:
    init_file = '{}/depsland/__init__.py'.format(depsland_root)
    with open(init_file, 'r') as f:
        for line in f.readlines():
            if line.startswith('__version__'):
                # "__version__ = '0.9.0b5'" -> ver0 = (0, 9, 0); ver1 = ('b', 5)
                m = re.search(r'\'(\d+)\.(\d+)\.(\d+)([ab]\d+)?\'', line)
                a, b, c, d = m.groups()
                ver0 = (int(a), int(b), int(c))
                ver1 = None if d is None else (d[0], int(d[1:]))
                break
        else:
            raise Exception
    if ver0 > (0, 9, 0):
        return True
    elif ver0 == (0, 9, 0):
        # noinspection PyTypeChecker
        if ver1 is None or ver1 >= ('b', 16):
            return True
    return False


def _run_app(
    depsland_root: str, appid: str, version: str, show_console: bool
) -> None:
    os.environ['PYTHONBREAKPOINT'] = '0'
    os.environ['PYTHONPATH'] = '.;chore/site_packages'
    os.environ['PYTHONUTF8'] = '1'
    print('change working directory to "{}"'.format(depsland_root))
    os.chdir(depsland_root)
    # python = {
    #     # (is_windows, is_atty): path
    #     (True, True): '.\\python\\python.exe',
    #     (True, False): '.\\python\\pythonw.exe',
    #     (False, True): './python/bin/python3',
    #     (False, False): './python/bin/python3w',
    # }[(os.name == 'nt', sys.stdin.isatty())]
    # if not show_console and sys.stdin.isatty():
    #     show_console = True
    python = (
        '.\\python\\python.exe' if show_console else '.\\python\\pythonw.exe'
    )
    print('run command: {} -m depsland runx {} {}'.format(
        python, appid, version
    ))
    subprocess.run(
        (python, '-m', 'depsland', 'runx', appid, version)
    )


if __name__ == '__main__':
    main()
