import os
import typing as t
from collections import defaultdict

from lk_utils import fs

from .. import paths


class T:
    NameId = str
    NameIds = t.Iterable[NameId]
    AbsPath = str
    RelPath = str
    Ownership = t.Dict[RelPath, NameId]


def link_venv(
    name_ids: T.NameIds, venv_dir: T.AbsPath, overwrite: bool = None
) -> None:
    dirname_2_name_ids = defaultdict(list)
    for nid in name_ids:
        dir_ = _name_id_2_path(nid)
        # print(nid, dir_, len(os.listdir(dir_)), ':v')
        for dname in os.listdir(dir_):
            if dname == '__pycache__':
                continue
            dirname_2_name_ids[dname].append(nid)
    if not dirname_2_name_ids:
        print('no package to link to venv', ':p')
        fs.make_dirs(venv_dir)
        return
    
    ownership: T.Ownership = {}
    for dname, name_ids in dirname_2_name_ids.items():
        if len(name_ids) == 1:
            ownership[dname] = name_ids[0]
        else:
            ownership.update(_divide_ownerships(dname, name_ids))
    
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
    relpath: T.RelPath, candidates: T.NameIds
) -> T.Ownership:
    """
    docs: docs/devnote/merge-links-algorithm.zh.md
    """
    file_asset_2_name_ids = defaultdict(list)
    dir_asset_2_name_ids = defaultdict(list)
    relpath_2_name_id = {}
    
    for nid in candidates:
        dir_ = '{}/{}'.format(_name_id_2_path(nid), relpath)
        for asset in fs.find_dirs(dir_):
            if asset.name == '__pycache__':
                continue
            dir_asset_2_name_ids[asset.name].append(nid)
        for asset in fs.find_files(dir_):
            file_asset_2_name_ids[asset.name].append(nid)
    
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
    print(dirs_to_be_created, ':lv')
    if '.' in dirs_to_be_created:
        dirs_to_be_created.remove('.')
    for relpath in sorted(dirs_to_be_created):
        abspath = f'{root_dir}/{relpath}'
        fs.make_dirs(abspath)


def _name_id_2_path(name_id: T.NameId) -> T.AbsPath:
    name, ver = name_id.split('-', 1)
    return '{}/{}/{}'.format(paths.pypi.installed, name, ver)
