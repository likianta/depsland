import typing as tp

from lk_utils import fs

from ..utils import hash_text


class T:
    FolderSnapshot = tp.TypedDict(
        'FolderSnapshot',
        {'dirs': tp.Dict[str, int], 'files': tp.Dict[str, int]},
    )


def check_folder_changed(path: str) -> bool:
    cache_file = fs.there(
        '../_cache/folder_snapshot/{}.pkl'.format(hash_text(path))
    )
    if fs.exist(cache_file):
        base: T.FolderSnapshot = fs.load(cache_file)
        for d in fs.findall_dirs(path):
            if d.relpath not in base['dirs']:
                return True
            elif fs.filetime(d.path) != base['dirs'][d.relpath]:
                return True
        for f in fs.findall_files(path):
            if f.relpath not in base['files']:
                return True
            elif fs.filetime(f.path) != base['files'][f.relpath]:
                return True
        return False
    else:
        fs.dump(_snapshot_folder(path), cache_file)
        return True


def _snapshot_folder(path: str) -> T.FolderSnapshot:
    out = {'dirs': {}, 'files': {}}
    for d in fs.findall_dirs(path):
        out['dirs'][d.relpath] = fs.filetime(d.path)
    for f in fs.findall_files(path):
        out['files'][f.relpath] = fs.filetime(f.path)
    return out  # type: ignore
