import os

from lk_utils import run_cmd_args

if os.name == 'nt':
    py = 'python/python.exe'
else:
    py = 'python/bin/python3'

run_cmd_args(
    py, '-m', 'pip', 'install', '-r', 'requirements.txt',
    '--find-links', 'chore/custom_packages',
    '--disable-pip-version-check', '--no-warn-script-location',
    verbose=True
)
