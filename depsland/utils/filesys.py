import typing as tp

from lk_utils import fs

from ..paths import temp


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
        return temp.make_unique_dir(custom_dirname)
    else:
        return temp.make_dir()
