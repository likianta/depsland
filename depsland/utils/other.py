import hashlib
import os
from packaging.version import Version
from uuid import uuid1
from ..paths import temp_dir


def compare_version(v0: str, comp: str, v1: str) -> bool:
    v0, v1 = map(Version, (v0, v1))
    if eval(f'v0 {comp} v1', {'v0': v0, 'v1': v1}):
        return True
    return False


def create_temporary_directory(root=temp_dir) -> str:
    out = f'{root}/{uuid1().hex}'
    os.mkdir(out)
    print(':vp', 'a temp dir is created', out)
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
