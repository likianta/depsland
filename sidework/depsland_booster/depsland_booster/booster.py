import os
import subprocess
import sys


def boost() -> None:
    self_file = sys.argv[0].replace('\\', '/')
    self_root = os.path.dirname(self_file)
    self_name = os.path.basename(self_file)
    if os.path.exists(x := f'{self_root}/.{self_name}.bat'):
        subprocess.run((x, *sys.argv[1:]), shell=True)
    else:
        print('[depsland-booster]', f'{sys.argv =}')
        print('[depsland-booster]', f'no bat file found for {self_name}')
