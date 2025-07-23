import os
import re
import subprocess
import typing as t


def main(
    appid: str = '<APPID>',
    version: str = '<VERSION>',
) -> None:
    if root := _find_depsland_root():
        # print(root, sys.argv)
        if _check_depsland_version(root):
            _run_app(root, appid, version)
    else:
        raise NotImplementedError


def _find_depsland_root() -> t.Optional[str]:
    # (A)
    if x := os.getenv('DEPSLAND'):
        # print(x)
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


# DELETE
def _find_depsland_executeable() -> t.Optional[str]:
    # (A)
    if x := os.getenv('DEPSLAND'):
        # print(x)
        if os.path.exists(x := '{}/apps/.bin/depsland.exe'.format(x)):
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
            return None
        else:
            winreg.CloseKey(key)
            if os.path.exists(x := '{}/apps/.bin/depsland.exe'.format(value)):
                return x
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
        if ver1 is None or ver1 >= ('b', 5):
            return True
    return False


def _run_app(depsland_root: str, appid: str, version: str) -> None:
    os.environ['PYTHONBREAKPOINT'] = '0'
    os.environ['PYTHONPATH'] = '.;chore/site_packages'
    os.environ['PYTHONUTF8'] = '1'
    print('change working directory to "{}"'.format(depsland_root))
    os.chdir(depsland_root)
    subprocess.run(
        ('.\\python\\python.exe', '-m', 'depsland', 'runx', appid, version)
    )


if __name__ == '__main__':
    main()
