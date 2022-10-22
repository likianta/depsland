from os import remove
from os.path import exists

from lk_logger import lk

from depsland.paths import pypi_model

for i in pypi_model.get_indexed_files():
    if exists(i):
        lk.loga('removing', i)
        remove(i)
    # if exists(i.replace('.pkl', '.json')):
    #     lk.loga('removing', i)
    #     remove(i)
