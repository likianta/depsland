import os
import typing as tp
from collections import namedtuple

from lk_utils import fs

from .typing import T
from ..utils import hash_content
from ..utils import hash_file_content

AssetInfo = namedtuple('AssetInfo', T.AssetInfo._fields)


def index_assets(
    assets0: T.Assets0, start_directory: T.StartDirectory
) -> T.Assets1:
    """
    doc: @wiki/src/devnote/manifest-assets-path-forms.md
    variable abbreviations:
        ftype: file type
        rpath or relpath: relative path
        utime: updated time
    """
    out = {}
    for rpath, scheme in _unpack_assets(assets0, start_directory):
        abspath = fs.normpath(f'{start_directory}/{rpath}')
        relpath = '' if rpath == '.' else fs.normpath(rpath)
        if not fs.exist(abspath):
            raise FileNotFoundError(
                'please check the path you defined in manifest does exist',
                rpath,
            )
        ftype = 'file' if os.path.isfile(abspath) else 'dir'
        out[relpath] = AssetInfo(
            type=ftype,
            scheme=scheme,
            utime=_generate_utime(abspath, scheme),
            hash=_generate_hash(abspath, ftype),
            uid=_generate_uid(ftype, relpath),
        )
    return out


def _generate_hash(abspath: str, ftype: str) -> str:
    if ftype == 'file':
        return hash_file_content(abspath)
    # if calculate_dir_hash:
    #     meta_info = []
    #     for d in fs.findall_dirs(abspath):
    #         meta_info.append('dir:{}'.format(d.relpath))
    #     for f in fs.findall_files(abspath):
    #         meta_info.append('file:{}:{}'.format(
    #             f.relpath, os.path.getsize(f.path)
    #         ))
    #     return hash_content('\n'.join(meta_info))
    return ''


def _generate_uid(ftype: str, rpath: str) -> str:
    return hash_content(f'{ftype}:{rpath}')


def _generate_utime(abspath: str, scheme: T.AssetScheme) -> int:
    if os.path.isfile(abspath):
        return int(os.path.getmtime(abspath))
    elif os.path.islink(abspath):
        abspath = os.path.realpath(abspath)
    else:
        assert os.path.isdir(abspath), abspath
        #   if assertion error, this abspath may not exist.

    mtime = int(os.path.getmtime(abspath))
    recursive = scheme is None or scheme == 0b11
    if recursive and os.listdir(abspath):
        # https://stackoverflow.com/questions/29685069

        def _walk(entrance: str) -> tp.Iterator[str]:
            yield from (x.path for x in fs.findall_dirs(entrance))
            yield from (x.path for x in fs.findall_files(entrance))

        return max(
            (mtime, max(map(int, map(os.path.getmtime, _walk(abspath)))))
        )
    else:
        return mtime


def _unpack_assets(
    assets: T.Assets0, start_directory: T.StartDirectory
) -> tp.Iterator[tp.Tuple[T.RelPath, T.AssetScheme]]:
    def resolve_wildcard(
        rpath: str, scheme: T.AssetScheme
    ) -> tp.Iterator[tp.Tuple[T.RelPath, T.AssetScheme]]:
        path0, path1 = rpath, rpath.rstrip('/*')
        if scheme is None:
            dirpath = fs.normpath('{}/{}'.format(start_directory, path1))
            for d in fs.find_dirs(dirpath):
                yield fs.relpath(d.path, start_directory), None
            if path0.endswith('/*'):
                for f in fs.find_files(dirpath):
                    yield fs.relpath(f.path, start_directory), None
        elif scheme == 0b11:
            print(
                'glob pattern can be simplified: {}:11 -> {}:11'.format(
                    path0, path1
                ),
                ':v5r2',
            )
            yield path1, 0b11
        else:
            dirpath = fs.normpath('{}/{}'.format(start_directory, path1))
            for d in fs.find_dirs(dirpath):
                yield fs.relpath(d.path, start_directory), scheme

    scheme: T.AssetScheme
    for raw_path in assets:
        if raw_path.endswith((':0', ':00', ':1', ':01', ':10', ':11')):
            rpath, x = raw_path.rsplit(':', 1)
            scheme = int(x, 2)
        else:
            rpath = raw_path
            scheme = None

        if rpath.endswith(('/*', '/*/')):
            yield from resolve_wildcard(rpath, scheme)
        else:
            yield rpath, scheme
