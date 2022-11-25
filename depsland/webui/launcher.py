import atexit
import socket
import subprocess
from contextlib import closing
from datetime import datetime
from subprocess import PIPE

import webview  # pip install pywebview
from lk_utils import xpath


def main() -> None:
    """
    launch streamlit in a subprocess, while showing a local-host web page
    within native window.
    """
    host = _get_ip_address()
    port = _get_free_port()
    print(host, port)
    _start_streamlit(host, port)
    _show_window(host, port)


def _get_ip_address() -> str:
    host = socket.gethostname()  # -> e.g. 'likianta-mibook-15-pro'
    ip = socket.gethostbyname(host)  # -> e.g. '192.168.10.102'
    return ip


def _get_free_port(start_at=8501) -> int:
    """
    https://stackoverflow.com/questions/1365265
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        for i in range(start_at, 65535):
            try:
                s.bind(('', i))
            except OSError:
                continue
            else:
                return i
    raise Exception('no free port available!')


def _start_streamlit(host: str, port: int) -> None:
    print('starting streamlit app...')
    proc = subprocess.Popen((
        'streamlit', 'run', xpath('home.py'),
        '--browser.serverAddress', host,
        '--browser.serverPort', str(port),
        '--server.headless', 'true',
    ), stdout=PIPE, stderr=PIPE, text=True)
    atexit.register(proc.kill)


def _show_window(host: str, port: int) -> None:
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
    webview.start()


if __name__ == '__main__':
    main()
