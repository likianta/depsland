import os
import shlex
import subprocess
import sys
import typing as t

import lk_logger
from argsense import args_2_cargs
from lk_utils import fs
from lk_utils import run_cmd_args

from ... import paths
from ...manifest import get_last_installed_version
from ...manifest import load_manifest
from ...platform import sysinfo


def run_app(
    appid: str = None,
    *args,
    _caller_location: str = None,
    _version: str = None,
    _blocking: bool = True,
    **kwargs
) -> t.Optional[subprocess.Popen]:
    """
    a general launcher to start an installed app.
    
    related:
        /depsland/__main__.py
        /build/exe/depsland-runapp.bat
    """
    if appid is None:
        assert (
            _caller_location and _caller_location.endswith(('.exe', '.bat'))
        ), _caller_location
        # related:
        #   depsland.api.user_api.install._create_launchers
        #   build/exe/depsland-runapp.bat
        #   build/exe/depsland-runapp-debug.bat
        #   build/build.py : [code] if __name__ == '__main__' : [comment]
        caller_dir = fs.parent(_caller_location)
        _, appid, _version = caller_dir.rsplit('/', 2)
        print(_caller_location, appid, _version)
    
    version = _version or get_last_installed_version(appid)
    if not version:
        print(':v8', f'cannot find installed version of {appid}')
        return
    else:
        print(
            ':r', '[magenta dim]launching [cyan]{}[/] [green]v{}[/][/]'
            .format(appid, version)
        )
    
    manifest = load_manifest('{}/{}/{}/manifest.pkl'.format(
        paths.project.apps, appid, version
    ))
    assert manifest['version'] == version
    os.environ['DEPSLAND'] = paths.project.root
    # note (2025-09-04):
    #   we don't need the following code (thus they are commented).
    #   further more explanation:
    #       the embeddable python interpreter is running in an isolated mode, -
    #       so it doesn't add cwd to sys.path, also ignores PYTHONPATH setting.
    #       we have resolved this problem by modifying -
    #       `/python/python312._pth` file, while the following code won't -
    #       work, we commented it.
    # sep = ';' if sysinfo.IS_WINDOWS else ':'
    # os.environ['PYTHONPATH'] = sep.join((
    #     '.',  # "current" dir
    #     'lib',  # frequently used dir
    #     'src',  # frequently used dir
    #     manifest['start_directory'],  # app_dir
    #     paths.apps.get_venv_dir(appid, version),  # pkg_dir
    # ))
    # print(
    #     os.environ['PYTHONPATH'].split(sep),
    #     os.environ['PATH'].split(sep), ':lv'
    # )
    
    if not manifest['launcher']['show_console']:
        if sysinfo.IS_WINDOWS:
            _toast_notification(
                'Depsland is launching "{} (v{})"'.format(appid, version)
            )
    
    command = '{} {}'.format(
        # FIXME: literally replacing "python" is not reliable.
        manifest['launcher']['command'].replace(
            'python', '"{}"'.format(sys.executable.replace('\\', '/')), 1
        ),
        shlex.join(args_2_cargs(*args, **kwargs))
    ).strip()
    print(':vs', command)
    # lk_logger.unload()
    try:
        return run_cmd_args(
            shlex.split(command),
            cwd=manifest['start_directory'],
            blocking=_blocking,
            shell=True,
            verbose=True,
        )
    except Exception as e:
        lk_logger.enable()
        print(':e', e)
        if manifest['launcher']['show_console']:
            # raise e
            input('press ENTER to exit... ')
        else:
            _popup_error_2(
                'Exception occurred in "{}"!'.format(manifest['name'])
            )


# DELETE
def _popup_error(msg: str) -> None:
    """ use tkinter popup to show error message. """
    import tkinter
    from tkinter import messagebox
    root = tkinter.Tk()
    root.withdraw()
    messagebox.showerror('Depsland Run Failed', msg)
    root.destroy()


def _popup_error_2(msg: str) -> None:
    # https://stackoverflow.com/a/4485736/9695911
    import ctypes
    box = ctypes.windll.user32.MessageBoxW  # noqa
    box(None, msg, 'Depsland Run Failed', 0)


# windows only  # DELETE: the toast sound is annoying for user.
def _toast_notification(text: str) -> None:
    try:
        from windows_toasts import Toast
        from windows_toasts import WindowsToaster
    except ImportError:
        # raise ImportError('pip install windows-toasts')
        print('module not found: windows-toasts', ':v6p')
        return
    toaster = WindowsToaster('Depsland Launcher')
    toast = Toast()
    toast.text_fields = [text]
    toaster.show_toast(toast)
