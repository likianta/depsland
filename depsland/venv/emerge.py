import os
import typing as t
from collections import defaultdict

# from lk_utils import Signal
from lk_utils import fs

from .. import paths


class T:
    AbsPath = str
    RelPath = str
    PackageId = str
    
    Ownership = t.Dict[RelPath, PackageId]
    PackageIds = t.Iterable[PackageId]


def link_venv(
    pkg_ids: T.PackageIds,
    venv_dir: T.AbsPath,
    overwrite: bool = None,
    # _signal: Signal[int] = None
) -> None:
    dirname_2_name_ids = defaultdict(list)
    for pid in pkg_ids:
        dir_ = _name_id_2_path(pid)
        # print(pid, dir_, len(os.listdir(dir_)), ':v')
        for dname in os.listdir(dir_):
            if dname == '__pycache__':
                continue
            dirname_2_name_ids[dname].append(pid)
    if not dirname_2_name_ids:
        print('no package to link to venv', ':p')
        fs.make_dirs(venv_dir)
        return
    
    ownership: T.Ownership = {}
    for dname, pkg_ids in dirname_2_name_ids.items():
        if len(pkg_ids) == 1:
            ownership[dname] = pkg_ids[0]
        else:
            ownership.update(_divide_ownerships(dname, pkg_ids))
    
    _init_dirs(venv_dir, ownership.keys())
    for relpath, name_id in sorted(
        ownership.items(), key=lambda x: x[1]  # sort by name_id.
    ):
        print(name_id, relpath, ':vs')
        fs.make_link(
            '{}/{}'.format(_name_id_2_path(name_id), relpath),
            '{}/{}'.format(venv_dir, relpath),
            overwrite=overwrite,
        )


def _divide_ownerships(
    relpath: T.RelPath, candidates: T.PackageIds
) -> T.Ownership:
    """
    docs: docs/devnote/merge-links-algorithm.zh.md
    """
    file_asset_2_name_ids = defaultdict(list)
    dir_asset_2_name_ids = defaultdict(list)
    relpath_2_name_id = {}
    
    for pid in candidates:
        dir_ = '{}/{}'.format(_name_id_2_path(pid), relpath)
        for asset in fs.find_dirs(dir_):
            if asset.name == '__pycache__':
                continue
            dir_asset_2_name_ids[asset.name].append(pid)
        for asset in fs.find_files(dir_):
            file_asset_2_name_ids[asset.name].append(pid)
    
    for name, name_ids in file_asset_2_name_ids.items():
        if len(name_ids) > 1:
            print(
                'multiple owners claimed for one file '
                '(will choose the first one)',
                name, name_ids, ':v3',
            )
        relpath_2_name_id[f'{relpath}/{name}'] = name_ids[0]
    
    for name, name_ids in dir_asset_2_name_ids.items():
        if len(name_ids) > 1:
            print(
                '[yellow dim]multiple owners claimed for one dir '
                '(will merge them)[/]',
                name, name_ids, ':rv',
            )
            relpath_2_name_id.update(
                _divide_ownerships(f'{relpath}/{name}', name_ids)
            )
        else:
            relpath_2_name_id[f'{relpath}/{name}'] = name_ids[0]
    
    return relpath_2_name_id


def _init_dirs(root_dir: T.AbsPath, paths: t.Iterable[T.RelPath]) -> None:
    dirs_to_be_created = set(fs.parent_path(x) for x in paths)
    if '.' in dirs_to_be_created:
        dirs_to_be_created.remove('.')
    print(sorted(dirs_to_be_created), ':lv')
    for relpath in sorted(dirs_to_be_created):
        abspath = f'{root_dir}/{relpath}'
        fs.make_dirs(abspath)


def _name_id_2_path(name_id: T.PackageId) -> T.AbsPath:
    name, ver = name_id.split('-', 1)
    return '{}/{}/{}'.format(paths.pypi.installed, name, ver)
