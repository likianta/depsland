"""
to compile:
    cd sidework/mini_launcher/by_nuitka
    por nuitka --standalone --onefile main.py
    # will generate "main.exe" and so on.
"""
import os
import re
import subprocess
import sys
import typing as t


def main() -> None:
    if exe := _find_depsland_executeable():
        # print(exe, sys.argv)
        if _check_depsland_version(exe):
            subprocess.run([exe] + sys.argv[1:])
            pass
    else:
        raise NotImplementedError


def _find_depsland_executeable() -> t.Optional[str]:
    # currdir = os.path.normpath('{}/..'.format(__file__))
    # if os.path.exists(x := '{}/source/apps/.bin/depsland.exe'.format(currdir)):
    #     return x
    if x := os.getenv('DEPSLAND'):
        # print(x)
        assert os.path.exists(y := '{}/apps/.bin/depsland.exe'.format(x))
        return y


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
