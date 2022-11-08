import hashlib
import os
from uuid import uuid1

from .. import paths

_temp_dir = paths.project.temp


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
    if os.path.isfile(path):
        return int(os.path.getmtime(path))
    if os.path.islink(path):
        path = os.path.realpath(path)
    assert os.path.isdir(path), path  # if assertion error, it may because this
    #   path not exists
    mtime = int(os.path.getmtime(path))
    if not os.listdir(path):
        return mtime
    else:
        # https://stackoverflow.com/questions/29685069/get-the-last-modified
        # -date-of-a-directory-including-subdirectories-using-pytho
        return max((mtime, max(map(int, map(
            os.path.getmtime, (root for root, _, _ in os.walk(path))
        )))))


def make_temp_dir(root=_temp_dir) -> str:
    random_name = uuid1().hex
    out = f'{root}/{random_name}'
    os.mkdir(out)
    print(':vp', 'a temp dir is created', f'<depsland>/temp/{random_name}')
    return out
