"""
commands:
    A: launch backend server and frontend window
        py depsland/webui/launcher.py run
        py depsland/webui/launcher.py run localhost 8501
    B: launch backend server and frontend window separately
        py depsland/webui/launcher.py run --not-show-window
        py depsland/webui/launcher.py run localhost --not-show-window
        py depsland/webui/launcher.py run --port 8501 --not-show-window
        py depsland/webui/launcher.py show-window
"""
import atexit
import socket
import subprocess
from contextlib import closing
from datetime import datetime
from subprocess import PIPE

import lk_logger
import webview  # pip install pywebview
from argsense import cli
from lk_utils import new_thread
from lk_utils import run_cmd_args
from lk_utils import xpath

# lk_logger.unload()
lk_logger.setup(show_varnames=True)


@cli.cmd()
def run(host: str = None, port: int = None,
        show_window=True, debug=True) -> None:
    """
    launch streamlit in a subprocess, while showing a local-host web page -
    within native window.
    """
    host = host or _get_ip_address()
    port = port or _get_free_port()
    print(host, port)
    
    if show_window:
        _request_to_show_window_2(host, port)
    
    # _start_idom(host, port)
    _start_idom_2(host, port, debug)
    # _start_streamlit(host, port)


def _get_ip_address() -> str:
    host = socket.gethostname()  # -> e.g. 'likianta-mibook-15-pro'
    ip = socket.gethostbyname(host)  # -> e.g. '192.168.10.102'
    return ip


def _get_free_port(start=8501, end=65535) -> int:
    """
    https://stackoverflow.com/questions/1365265
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        for i in range(start, end):
            try:
                s.bind(('', i))
            except OSError:
                continue
            else:
                return i
    raise Exception('no free port available!')


# -----------------------------------------------------------------------------

def _request_to_show_window(host: str, port: int, debug=False) -> None:
    subprocess.run((
        'py', __file__, 'show-window', host, str(port),
        '--debug' if debug else ''
    ), stdout=PIPE, stderr=PIPE, text=True, check=True)


@new_thread()
def _request_to_show_window_2(host: str, port: int) -> None:
    run_cmd_args(
        'py', __file__, 'show-window', host, str(port), verbose=True
    )


# -----------------------------------------------------------------------------

def _start_idom(host: str, port: int) -> None:
    print('starting idom app')
    
    proc = subprocess.Popen((
        'py', xpath('home_idom.py'), host, str(port),
    ), stdout=PIPE, stderr=PIPE, text=True)
    
    for line in proc.stdout:
        print(line.rstrip())
    for line in proc.stderr:
        print(line.rstrip())
    
    atexit.register(proc.kill)


def _start_idom_2(host: str, port: int, debug: bool) -> None:
    from depsland.webui.home_idom import run
    run(host, port, debug=debug)


def _start_streamlit(host: str, port: int) -> None:
    print('starting streamlit app')
    proc = subprocess.Popen((
        'streamlit', 'run', xpath('home_st.py'),
        '--browser.serverAddress', host,
        '--browser.serverPort', str(port),
        '--server.headless', 'true',
    ), stdout=PIPE, stderr=PIPE, text=True)
    atexit.register(proc.kill)


# -----------------------------------------------------------------------------

@cli.cmd()
def show_window(host: str, port: int, debug=False) -> None:
    """
    this must be run in main thread.
    """
    
    def is_light_or_dark_theme() -> bool:
        """
        a very fuzzy method based on current time clock to determine whether to
        use light or dark theme.
        TODO: better to find an internal method from streamlit to know how it
            changes itself theme.
        return:
            the boolean value is better to understand with its int-type meaning:
                0 (aka False): light
                1 (aka True): dark
        """
        now = datetime.now()
        return now.hour > 18 or now.hour < 6
    
    webview.create_window(
        'Depsland', f'http://{host}:{port}',
        background_color='#0F1116' if is_light_or_dark_theme() else '#FFFFFF',
    )
    # win.load_css(loads(xpath('bulma.min.css')))
    webview.start(debug=debug)


if __name__ == '__main__':
    cli.run()
    # main()
