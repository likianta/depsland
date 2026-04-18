"""
note: this script uses only standard libraries.
we can compile this into general purpose executable binary by nuitka. see
`./factory.py : build_general_launcher`.
"""
import json
import os
import subprocess
import sys
import typing as tp
import urllib.request
import zipfile

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
    conf = _get_config()
    if root := _find_depsland_root():
        # if _check_depsland_version(root):
        _run_app(root, conf['appid'], conf['version'], conf['show_console'])
    else:
        # download and install depsland
        # this operation should be fast to ensure user experience. so we 
        # download a $[** small-sized] executable file, then run it to connect 
        # to a remote GUI service for the complete installation.
        # see also $[./depsland_online_installer/readme.zh.txt].
        # print(
        #     'download depsland online installer',
        #     'http://172.20.128.100:2188/depsland_online_installer.exe',
        #     os.path.dirname(sys.argv[0]),
        #     conf
        # )

        def _update_progress(
            count: int, block_size: int, total_size: int
        ) -> None:
            print(
                'download depsland online installer progress: {:.2f}MB {:.2%}'
                .format(
                    total_size / 1024 / 1024, 
                    count * block_size / total_size
                ),
                end='\r'
            )

        currdir = os.path.dirname(sys.argv[0])
        urllib.request.urlretrieve(
            'http://172.20.128.100:2188/depsland_online_installer.zip',
            file := f'{currdir}/depsland_online_installer.zip',
            reporthook=_update_progress
        )
        print('')

        # print(file)
        # subprocess.run((file, conf['appid'], conf['version']))
        
        print(file)
        with zipfile.ZipFile(file, 'r') as f:
            f.extractall(f'{currdir}/depsland_online_installer_source')
        os.remove(file)

        # print(
        #     sys.executable, 
        #     os.path.exists(sys.executable),
        #     f'{currdir}/depsland_online_installer_source/dist/main.py',
        # )
        # print(
        #     subprocess.run(
        #         (sys.executable, '-V'), check=True, capture_output=True
        #     ).stdout.decode('utf-8')
        # )
        # subprocess.run(
        #     (
        #         sys.executable, 
        #         f'{currdir}/depsland_online_installer_source/dist/main.py'
        #     )
        # )

        import psutil
        print(psutil.__path__)

        dps_dir = f'{currdir}/depsland_online_installer_source/dist'
        sys.path.append(f'{dps_dir}/minideps')
        sys.path.append(f'{dps_dir}/python312.zip')
        os.chdir(dps_dir)
        with open('main.py', 'r') as f:
            exec(f.read())

def _find_depsland_root() -> tp.Optional[str]:
    # (A)
    if x := os.getenv('DEPSLAND'):
        if os.path.exists('{}/apps/.bin/depsland.exe'.format(x)):
            return x
    # (B)
    #   consider that the A method may fail because current session didn't -
    #   update itself to sync with system environment settings, so we read the -
    #   registry key directly to get the latest env variable.
    # if os.name == 'nt':
    #     import winreg
    #     key = winreg.OpenKey(
    #         winreg.HKEY_CURRENT_USER,
    #         'Environment',
    #         0,
    #         winreg.KEY_READ
    #     )
    #     try:
    #         value, _ = winreg.QueryValueEx(key, 'DEPSLAND')
    #     except FileNotFoundError:
    #         value = None
    #     finally:
    #         winreg.CloseKey(key)
    #     if value and os.path.exists(
    #         '{}/apps/.bin/depsland.exe'.format(value)
    #     ):
    #         return value
    # return None

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
