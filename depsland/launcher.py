"""
TODO: rethink which situation to use this launcher, is it be used like as
    pyportable-installer's pylauncher?
    related: ./__main__.py > def run()
"""
import os
import subprocess
import sys
from importlib.util import find_spec
from textwrap import dedent

from . import paths


def run(appid: str, version: str, command: str, error_output='terminal'):
    app_dir = '{}/{}/{}'.format(paths.project.apps, appid, version)
    assert os.path.exists(app_dir)
    
    os.chdir(app_dir)
    sys.path.insert(0, paths.apps.get_packages(appid, version))
    sys.path.insert(0, app_dir)
    
    try:
        exec(dedent(command), globals(), locals())
    except Exception as e:
        _show_error(str(e), output=error_output)


def _show_error(
        msg: str,
        title='Runtime Exception',
        output='terminal'
) -> None:
    """
    args:
        output:
            terminal: show error message in terminal.
            messagebox: show error message in a messagebox (os dependent).

    rerferences:
        https://stackoverflow.com/questions/2963263/how-can-i-create-a-simple
        -message-box-in-python
        https://stackoverflow.com/questions/1278705/when-i-catch-an-exception
        -how-do-i-get-the-type-file-and-line-number
        https://stackoverflow.com/questions/17280637/tkinter-messagebox-without
        -window
        https://www.cnblogs.com/freeweb/p/5048833.html
    """
    if output == 'terminal':
        print(title + ':', msg)
        input('press enter to leave...')
        sys.exit(1)
    else:  # output == 'messagebox':
        if find_spec('tkinter'):
            from tkinter import Tk, messagebox
            root = Tk()
            root.withdraw()
            messagebox.showerror(title=title, message=msg)
        else:
            if os.name == 'nt':
                subprocess.call(['msg', '*', title + ': ' + msg])
            else:
                subprocess.call([
                    'osascript',
                    '-e',
                    'Tell application "System Events" to display dialog "{{}}" '
                    'with title "{{}}"'.format(msg, title)
                ])
