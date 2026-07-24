import typing as tp
from collections import defaultdict

from lk_utils import fs
from lk_utils import uuid

from .manifest import T as T0
from .paths import cache as cache_paths
from .utils import hash_text


class T:
    Encryption = T0.Encryption1
    FolderSnapshot = tp.TypedDict(
        'FolderSnapshot',
        {
            'root_mtime': int,
            'dirs': tp.Dict[str, int],
            'files': tp.Dict[str, int],
        },
    )
    FolderTime = int
    RelPath = str
    ProjectCache = tp.TypedDict(
        'ProjectCache',
        {
            'encryption': tp.Optional[
                tp.TypedDict(
                    'Encryption',
                    {
                        'key_hash': str,
                        'packages': tp.Dict[RelPath, FolderTime],
                        'output': RelPath,
                    },
                )
            ]
        },
    )


_cached_results = defaultdict(dict)


def cache(namespace: str) -> tp.Callable:
    def wrapper(func: tp.Callable) -> tp.Callable:
        def call(folder: str) -> tp.Any:
            if folder in _cached_results[namespace]:
                return _cached_results[namespace][folder]
            else:
                result = func(folder)
                _cached_results[namespace][folder] = result
                return result

        return call

    return wrapper


def clear_cache(namespace: str) -> None:
    _cached_results[namespace].clear()


def reset_cache(namespace: str, key: str, value: tp.Any) -> None:
    _cached_results[namespace][key] = value


# ------------------------------------------------------------------------------


@cache('folder_changes')
def check_folder_changed(folder: str) -> bool:
    file = '{}/{}.pkl'.format(cache_paths.folder_snapshot, uuid(folder))
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
        file = '{}/{}.pkl'.format(cache_paths.folder_snapshot, uuid(folder))
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


# ------------------------------------------------------------------------------


def is_project_cached(appid: str) -> bool:
    return fs.exist('{}/{}.pkl'.format(cache_paths.project_cache, appid))


def get_project_cache(
    appid: str, encryption: T.Encryption, start_directory: str
) -> T.ProjectCache:
    file = '{}/{}.pkl'.format(cache_paths.project_cache, appid)
    if fs.exist(file):
        return fs.load(file)
    else:
        out: T.ProjectCache
        if enc := encryption:
            out = {
                'encryption': {
                    'key_hash': hash_text(enc['key']),
                    'packages': {
                        p: fs.mtime(
                            '{}/{}'.format(start_directory, p), recursive=True
                        )
                        for p in enc['packages']
                    },
                    'output': enc['output'],
                }
            }
        else:
            out = {'encryption': None}
        fs.dump(out, file)
        return out


def save_project_cache(
    appid: str, encryption: T.Encryption, start_directory: str
) -> None:
    fs.dump(
        {
            'encryption': {
                'key_hash': hash_text(encryption['key']),
                'packages': {
                    p: fs.mtime(
                        '{}/{}'.format(start_directory, p), recursive=True
                    )
                    for p in encryption['packages']
                },
                'output': encryption['output'],
            }
        },
        '{}/{}.pkl'.format(cache_paths.project_cache, appid),
    )


# ------------------------------------------------------------------------------

_persistent_kv = fs.load(cache_paths.persistent_kv_pairs, default={})


def check_persistent_key_changed(key: str, val: tp.Any) -> bool:
    return val == _persistent_kv.get(key, None)


def save_persistent_key(key: str, val: tp.Any) -> None:
    if val != _persistent_kv.get(key, None):
        _persistent_kv[key] = val
        fs.dump(_persistent_kv, cache_paths.persistent_kv_pairs)
