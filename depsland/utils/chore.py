import hashlib
import os
from uuid import uuid1
from .. import paths

_temp_dir = paths.Project.temp


def create_temporary_directory(root=_temp_dir) -> str:
    random_name = uuid1().hex
    out = f'{root}/{random_name}'
    os.mkdir(out)
    print(':vp', 'a temp dir is created', f'<depsland>/temp/{random_name}')
    return out


def get_file_hash(filepath: str) -> str:
    """
    If file is too big, read the first 8192 bytes.
    https://blog.csdn.net/qq_26373925/article/details/115409308
    """
    file = open(filepath, 'rb')
    md5 = hashlib.md5()
    if os.path.getsize(filepath) > 3 * 1024 * 1024:
        md5.update(file.read(8192))
    else:
        md5.update(file.read())
    file.close()
    return md5.hexdigest()


def get_updated_time(path: str) -> int:
    return int(os.path.getmtime(path))
