import re

from lk_logger import lk
from lk_utils import find_files

from depsland.path_struct import pypi_struct
from depsland.utils import unzip_file

for fp, fn in find_files(pypi_struct.downloads,
                         fmt='zip', suffix=('.whl', '.tar.gz')):
    name_id = re.search(r'[^-]+-[^-]+', fn).group()
    lk.logax(fn, name_id)
    try:
        unzip_file(fp, pypi_struct.mkdir(name_id))
    except FileExistsError:
        continue
