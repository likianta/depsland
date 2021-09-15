import os

from lk_logger import lk
from lk_utils import find_dirs

from depsland.path_model import pypi_model

failed = []

for p, n in find_dirs(pypi_model.extraced, fmt='zip'):
    if n == '.gitkeep':
        continue
    if not os.listdir(p):
        lk.logax(n)
        try:
            os.remove(p)
        except PermissionError:
            failed.append(n)

if failed:
    lk.logd('removing failed because of PermissionError')
    lk.reset_count(len(failed))
    for n in failed:
        lk.logax(n)
