"""
Try all efforts to minimize the distribution size of Depsland, then extract
archived files on client side.

WIP: This module is not stable to use.
"""
import os
import shutil
import subprocess
import sys

sys.path.append(os.path.abspath(f'{__file__}/../..'))

# noinspection PyUnresolvedReferences
from minimal_setup.index import ResourcesIndex  # noqa

python_exe = sys.executable
res_idx = ...


def main():
    global res_idx
    res_idx = _indexing_resources()
    _extract()
    _setup_venv_packages()
    _clean()


def _indexing_resources():
    res_idx = ResourcesIndex()
    return res_idx


def _extract():
    def _extract(file_i: str, dir_o):
        if file_i.endswith(('.tar.gz', '.tar')):
            import tarfile
            file_handle = tarfile.open(file_i)
        else:
            from zipfile import ZipFile
            file_handle = ZipFile(file_i)
        file_handle.extractall(dir_o)
        return dir_o
    
    _extract(res_idx.assets_zip, res_idx.assets)
    _extract(res_idx.venv_packages_zip, res_idx.venv_packages_unzip)


def _setup_venv_packages():
    # note: assert pip and setuptools already exist
    send_cmd(f'{python_exe} -m pip install -r {res_idx.requirements} '
             f'--no-index -f {res_idx.venv_packages_unzip}')


def _clean():
    for i in (
            res_idx.assets_zip,
            res_idx.temp,
            res_idx.venv_packages_zip,
    ):
        if os.path.exists(i):
            if os.path.isfile(i):
                os.remove(i)
            else:
                shutil.rmtree(i)


# -----------------------------------------------------------------------------

def copy_dirs(dir_i, dir_o):
    for n in os.listdir(dir_i):
        i = f'{dir_i}/{n}'
        o = f'{dir_o}/{n}'
        shutil.copytree(i, o)


def send_cmd(cmd: str) -> str:
    try:
        ret = subprocess.run(
            cmd, shell=True, check=True, capture_output=True
        )
        out = ret.stdout.decode(encoding='utf-8').replace('\r\n', '\n')
    except subprocess.CalledProcessError as e:
        out = e.stderr.decode(encoding='utf-8')
        raise Exception(out)
    return out
