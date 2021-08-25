from os import remove
from os.path import exists

from lk_logger import lk

from depsland.path_struct import pypi_struct

for i in pypi_struct.get_indexed_files():
    if exists(i):
        lk.loga('removing', i)
        remove(i)