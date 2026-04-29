"""
what to do:
    1. update <tree_shaking_library>/patches/implicit_import_hooks.yaml
    2. run build
        $poetry run python run.py build
    3. run test
        $clean_python run.py test
    4. if error happens, read error message, restart from step 1
"""

import sys

sys.path.append('minideps')

import tree_shaking
from argsense import cli
from lk_utils import fs

fs.cd_current_dir()


@cli
def build():
    tree_shaking.build_module_graphs('tree_shaking.yaml')
    tree_shaking.dump_tree('tree_shaking.yaml')


@cli
def test():
    import py7zr  # type: ignore

    print(py7zr.__path__)

    file_i = 'test_in.7z'
    if not fs.exist(file_i):
        raise Exception(
            '"test_in.7z" not exists, you can manually build it by: '
            '\t$poetry run python -m lk_utils zip <any_folder_path> test_in.7z'
        )
    dir_o = 'test_out'
    fs.unzip(file_i, dir_o, overwrite=True, progress=True)


if __name__ == '__main__':
    cli.run()
