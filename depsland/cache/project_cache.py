import typing as tp
from functools import cache

from lk_utils import fs

from ..manifest import T as T0
from ..utils import hash_text

cache_dir = fs.here('_cache')


class T:
    FolderSnapshot = tp.TypedDict(
        'FolderSnapshot',
        {'dirs': tp.Dict[str, int], 'files': tp.Dict[str, int]},
    )
    Manifest = T0.Manifest
    ProjectCache = tp.TypedDict(
        'ProjectCache',
        {
            'last_encrypted_folders_snapshots': tp.Dict[str, FolderSnapshot],
            'last_encryption_key_(hash)': str,
        },
    )


@cache
def get_project_cache(appid: str) -> T.ProjectCache:
    if fs.exist(file := '{}/{}.pkl'.format(cache_dir, appid)):
        return fs.load(file)
    else:
        return {
            'last_encryption_key_(hash)': '',
            'last_encrypted_folders_snapshots': {},
        }


def save_project_cache(manifest: T.Manifest) -> None:
    if enc := manifest['encryption']:
        appid = manifest['appid']
        print('save project cache: _cache/{}.pkl'.format(appid), ':vp')
        cache_file = '{}/{}.pkl'.format(cache_dir, appid)
        fs.dump(
            {
                'last_encryption_key_(hash)': hash_text(enc['key']),
                'last_encrypted_folders_snapshots': {
                    pkg_path: _snapshot_folder(pkg_path)
                    for pkg_path in enc['packages']
                },
            },
            cache_file,
        )


def _snapshot_folder(path: str) -> T.FolderSnapshot:
    out = {'dirs': {}, 'files': {}}
    for d in fs.findall_dirs(path):
        out['dirs'][d.relpath] = fs.filetime(d.path)
    for f in fs.findall_files(path):
        out['files'][f.relpath] = fs.filetime(f.path)
    return out  # type: ignore
