import atexit
import hashlib
import os
import shutil
from uuid import uuid1

from .. import paths


def get_content_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


def get_file_hash(filepath: str) -> str:
    """
    if file is too big, read the first 8192 bytes.
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


def get_updated_time(path: str, recursive=False) -> int:
    if os.path.isfile(path):
        return int(os.path.getmtime(path))
    if os.path.islink(path):
        path = os.path.realpath(path)
    assert os.path.isdir(path), path  # if assertion error, it may because this
    #   path not exists
    mtime = int(os.path.getmtime(path))
    if recursive is False or not os.listdir(path):
        return mtime
    else:
        # https://stackoverflow.com/questions/29685069/get-the-last-modified
        # -date-of-a-directory-including-subdirectories-using-pytho
        return max((mtime, max(map(int, map(
            os.path.getmtime, (root for root, _, _ in os.walk(path))
        )))))


class _TempDirs:
    
    def __init__(self):
        self._root = paths.project.temp
        self._dirs = set()
        atexit.register(self.clean_up)
    
    def make_dir(self, root: str = None) -> str:
        root = root or self._root
        # assert os.path.exists(root)
        random_name = uuid1().hex
        temp_dir = f'{root}/{random_name}'
        os.mkdir(temp_dir)
        self._dirs.add(temp_dir)
        print(':vp', 'a temp dir is created', random_name)
        return temp_dir
    
    def clean_up(self) -> None:
        if self._dirs:
            print(':vs', 'clean up temp created dirs', len(self._dirs))
            for d in self._dirs:
                if os.path.exists(d):
                    shutil.rmtree(d)


_temp_dirs = _TempDirs()
make_temp_dir = _temp_dirs.make_dir
