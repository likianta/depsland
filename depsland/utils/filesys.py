import typing as tp

from lk_utils import fs
from lk_utils import uuid

from .. import paths
from ..cache import cache
from ..cache import reset_cache


class T:
    FolderSnapshot = tp.TypedDict(
        'FolderSnapshot',
        {
            'root_mtime': int,
            'dirs': tp.Dict[str, int],
            'files': tp.Dict[str, int],
        },
    )


def init_target_tree(root: str, relpath_dirs: tp.Iterable[str]) -> None:
    print('init making tree', root, ':np')
    paths_to_be_created = {root}
    paths_to_be_created.update((f'{root}/{x}' for x in relpath_dirs))
    paths_to_be_created = sorted(paths_to_be_created)
    # print(':vl', paths_to_be_created)
    for p in paths_to_be_created:
        fs.make_dirs(p)


def make_temp_dir(custom_dirname: str = '') -> str:
    if custom_dirname:
        return paths.temp.make_unique_dir(custom_dirname)
    else:
        return paths.temp.make_dir()


@cache('folder_changes')
def check_folder_changed(folder: str) -> bool:
    file = '{}/{}.pkl'.format(paths.cache.folder_snapshot, uuid(folder))
    if fs.exist(file):
        snapshot: T.FolderSnapshot = fs.load(file)
        if snapshot['root_mtime'] != fs.mtime(folder):
            return True
        else:
            for d in fs.findall_dirs(folder):
                if d.relpath not in snapshot['dirs']:
                    return True
                elif d.mtime != snapshot['dirs'][d.relpath]:
                    return True
            for f in fs.findall_files(folder):
                if f.relpath not in snapshot['files']:
                    return True
                elif f.mtime != snapshot['files'][f.relpath]:
                    return True
        return False
    else:
        return True


def save_folder_changes(folder: str) -> None:
    if check_folder_changed(folder):
        file = '{}/{}.pkl'.format(paths.cache.folder_snapshot, uuid(folder))
        snapshot: T.FolderSnapshot = {
            'root_mtime': tp.cast(int, fs.filetime(folder)),
            'dirs': {
                d.relpath: tp.cast(int, d.mtime)
                for d in fs.findall_dirs(folder)
            },
            'files': {
                f.relpath: tp.cast(int, f.mtime)
                for f in fs.findall_files(folder)
            },
        }
        fs.dump(snapshot, file)
        reset_cache('folder_changes', folder, False)
