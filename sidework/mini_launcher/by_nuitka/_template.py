"""
note: this script uses only standard libraries.
we can compile this into general purpose executable binary by nuitka. see
`./factory.py : build_general_launcher`.
"""
import json
import os
import re
import sys
import subprocess
import typing as tp

class T:
    Config = tp.TypedDict('Config', {
        'appid': str,
        'name': str,  # DELETE?
        'version': str,
        'show_console': bool,
    })

def _get_config() -> T.Config:
    # note: do not use `__file__`, use `sys.argv[0]`.
    #   because:
    #       sys.argv = [`some/path/to/exe`]
    #       __file__ = `AppData/Local/Temp/ONEFIL~1/general_launcher_console.py`
    with open(sys.argv[0], 'rb') as f:
        raw = f.read()
    conf_head_idx = raw.rfind(b'__DEPSLAND_CONFIG__')
    assert conf_head_idx > 0
    conf_body_idx = conf_head_idx + len(b'__DEPSLAND_CONFIG__')
    return json.loads(raw[conf_body_idx:].decode('utf-8'))

def main() -> None:
    # print(_find_depsland_root(), _get_config())
    if root := _find_depsland_root():
        # if _check_depsland_version(root):
        conf = _get_config()
        _run_app(root, conf['appid'], conf['version'], conf['show_console'])
        return
    raise NotImplementedError

def _find_depsland_root() -> tp.Optional[str]:
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
    if ver0 > (0, 11, 0):
        return True
    elif ver0 == (0, 11, 0):
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
