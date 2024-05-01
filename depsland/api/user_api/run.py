import os
import subprocess
import sys

import lk_logger
from argsense import args_2_cargs

from ... import paths
from ...manifest import get_last_installed_version
from ...manifest import load_manifest
from ...manifest import parse_script_info
from ...platform import sysinfo


def run_app(appid: str, *args, _version: str = None, **kwargs) -> None:
    """
    a general launcher to start an installed app.
    """
    version = _version or get_last_installed_version(appid)
    if not version:
        print(':v4', f'cannot find installed version of {appid}')
        return
    else:
        print(':r', '[magenta dim]depsland {} [green]v{}[/][/]'.format(
            ' '.join(sys.argv[1:]), version
        ))
    
    manifest = load_manifest(
        '{}/{}/{}/manifest.pkl'.format(paths.project.apps, appid, version)
    )
    assert manifest['version'] == version
    command, args0, kwargs0 = parse_script_info(manifest)
    # print(command, args0, kwargs0, ':l')
    os.environ['DEPSLAND'] = paths.project.root
    sep = ';' if sysinfo.IS_WINDOWS else ':'
    os.environ['PYTHONPATH'] = sep.join((
        '.',  # cur_dir
        manifest['start_directory'],  # app_dir
        paths.apps.get_packages(appid, version),  # pkg_dir
    ))
    # print(
    #     os.environ['PYTHONPATH'].split(sep),
    #     os.environ['PATH'].split(sep), ':lv'
    # )
    
    if not manifest['launcher']['show_console']:
        if sysinfo.IS_WINDOWS:
            _toast_notification(
                'Depsland is launching "{}"'.format(manifest['name'])
            )
    
    # print(':v', args, kwargs)
    lk_logger.unload()
    try:
        subprocess.run(
            # TODO: use '--' to separate different args/kwargs groups.
            (*command, *args_2_cargs(*args, *args0, **kwargs, **kwargs0)),
            check=True,
            cwd=manifest['start_directory'],
            stderr=subprocess.PIPE,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        lk_logger.enable()
        print(':v4f', '\n' + (e.stderr or '').replace('\r', ''))
        if manifest['launcher']['show_console']:
            # raise e
            input('press ENTER to exit... ')
        else:
            _toast_notification(
                'Exception occurred at "{}"!'.format(manifest['name'])
            )


# windows only
def _toast_notification(text: str) -> None:
    try:
        from windows_toasts import Toast
        from windows_toasts import WindowsToaster
    except ImportError:
        raise ImportError('pip install windows-toasts')
    toaster = WindowsToaster('Depsland Launcher')
    toast = Toast()
    toast.text_fields = [text]
    toaster.show_toast(toast)
