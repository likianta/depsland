import os
import shutil
import sys


def generate_exe(target: str) -> None:
    if os.path.isdir(target):
        root = os.path.abspath(target)
        name = os.path.basename(root)
        file = f'{root}/{name}.exe'
    else:
        assert target.endswith('.exe')
        file = os.path.abspath(target)
        name = os.path.basename(file)
    
    if os.path.exists(file):
        os.remove(file)
    shutil.copyfile(
        '{}/Scripts/depsland-booster.exe'
        .format(sys.base_exec_prefix),
        file
    )
    print(f'generated: {name}')


if __name__ == '__main__':
    generate_exe(sys.argv[1])
