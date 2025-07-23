import os
import re
import subprocess
import sys
import typing as t


def main(
    appid: str = '<APPID>',
    version: str = '<VERSION>',
) -> None:
    if exe := _find_depsland_executeable():
        # print(exe, sys.argv)
        if _check_depsland_version(exe):
            subprocess.run((exe, 'runx', appid, version))
            pass
    else:
        raise NotImplementedError


def _find_depsland_executeable() -> t.Optional[str]:
    # (A)
    # currdir = os.path.normpath('{}/..'.format(__file__))
    # if os.path.exists(x := '{}/source/apps/.bin/depsland.exe'.format(currdir)):
    #     return x
    # (B)
    if x := os.getenv('DEPSLAND'):
        # print(x)
        if os.path.exists(x := '{}/apps/.bin/depsland.exe'.format(x)):
            return x
    # (C)
    #   consider that the B method may fail because current session didn't -
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


def _check_depsland_version(exe_path: str) -> bool:
    init_file = os.path.normpath(
        '{}/../../../depsland/__init__.py'.format(exe_path)
    )
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


if __name__ == '__main__':
    main()
