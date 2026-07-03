import os
import typing as tp


def init_target_tree(root: str, relpath_dirs: tp.Iterable[str]) -> None:
    print('init making tree', root, ':p')
    paths_to_be_created = {root}
    paths_to_be_created.update((f'{root}/{x}' for x in relpath_dirs))
    paths_to_be_created = sorted(paths_to_be_created)
    # print(':vl', paths_to_be_created)
    for p in paths_to_be_created:
        os.makedirs(p, exist_ok=True)
