import re

from lk_utils import fs


def add_info_to_exe(file_exe: str, info: bytes):
    raw = fs.load(file_exe, 'binary')
    fs.dump(raw + b'__DEPSLAND_MAGIC__' + info, file_exe)


def bump_version(old: str) -> str:
    """
    bump the least part of the version.
    example:
        0.12.0   -> 0.12.1
        0.12.1a9 -> 0.12.1a10
        0.12.1b0 -> 0.12.1b1
    """
    a, b, c, d = re.match(r'(\d+)\.(\d+)\.(\d+)([ab]\d+)?', old).groups()
    if d is None:
        return f'{a}.{b}.{int(c) + 1}'
    else:
        return f'{a}.{b}.{c}{d[0]}{int(d[1:]) + 1}'
