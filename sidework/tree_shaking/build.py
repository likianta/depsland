import typing as t

from depsland.utils import init_target_tree
from lk_utils import fs
from lk_utils import p


def make_tree(dir_o: str) -> None:
    references: t.Dict[str, str] = fs.load(p('_references.yaml'))
    assert all(
        v.startswith('C:/Likianta/workspace/dev_master_likianta/depsland/')
        for v in references.values()
    )
    relpath_dirs = set()
    for k, v in references.items():
        relpath_dirs.add(fs.parent(v.removeprefix(
            'C:/Likianta/workspace/dev_master_likianta/depsland/'
        )))
    print(len(relpath_dirs))
    init_target_tree(dir_o, relpath_dirs)
    
    for v in set(references.values()):
        i = v
        o = '{}/{}'.format(dir_o, v.removeprefix(
            'C:/Likianta/workspace/dev_master_likianta/depsland/'
        ))
        fs.copy_file(i, o)
    print(
        len(references),
        len(relpath_dirs),
        len(set(references.values())),
    )
    print('done', ':t')
