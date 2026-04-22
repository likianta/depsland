from lk_utils import fs

def add_info_to_exe(file_exe: str, info: bytes):
    raw = fs.load(file_exe, 'binary')
    fs.dump(raw + b'__DEPSLAND_MAGIC__' + info, file_exe)
