import streamlit_canary as sc
import sys
from lk_utils import run_cmd_args

def run_all(bore_secret: str, debug: bool = False):
    start_airmise_proxy_server(blocking=False)
    start_streamlit_app(blocking=False)
    if debug:
        local_serve_resources(blocking=True)
    else:
        expose_service_to_public(bore_secret, blocking=True)

def expose_service_to_public(bore_secret: str, blocking: bool):
    bore_cmd = ('bore', 'local', '-s', bore_secret, '-t', '47.102.108.149')
    run_cmd_args(
        bore_cmd + ('-p', '2185', '2185'), verbose=True, blocking=False
    )
    run_cmd_args(
        bore_cmd + ('-p', '2186', '2186'), verbose=True, blocking=blocking
    )

def local_serve_resources(blocking: bool):
    run_cmd_args(
        (
            sys.executable, '-m', 'http.server', '-p', '2188', 
            '-d', 'resources'
        ), 
        verbose=True, 
        blocking=blocking,
    )

def start_airmise_proxy_server(blocking: bool):
    run_cmd_args(
        (
            sys.executable, 
            'depsland/gui/setup_wizard/depsland_installer_client_support.py', 
            'start-server'
        ),
        verbose=True, 
        blocking=blocking,
    )

def start_streamlit_app(blocking: bool):
    sc.run(
        'depsland/gui/setup_wizard/depsland_installer_online.py',
        port=2185,
        subthread=not blocking,
    )
