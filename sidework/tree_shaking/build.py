import os.path
import typing as t

from depsland.utils import init_target_tree
from lk_utils import fs
from lk_utils import p


class T:
    Data = t.TypedDict('Data', {
        'batch' : t.List[str],
        'single': t.List[str],
    })


def make_tree(file_i: str, dir_o: str) -> None:
    """
    file_i:
        data for example:
            batch:
              - sidework/tree_shaking/results/depsland-87b9e2b5.yaml
              - sidework/tree_shaking/results/streamlit-21376326.yaml
              - sidework/tree_shaking/results/toga-winforms-8fcc0710.yaml
            single:
              - chore/site_packages/streamlit/__init__.py
              - chore/site_packages/streamlit/__main__.py
              - depsland/__init__.py
              - depsland/__main__.py
              - depsland/chore/
        explanation:
            - use '/' to the end to indicate a directory.
            - all paths are absolute or relative (suggested) to current working
            directory (i.e. `os.getcwd()`).
    dir_o: an empty directory to store the tree. it can be an inexistent path.
    """
    data: T.Data = fs.load(file_i)
    
    files = set()  # a set of absolute paths
    dirs = set()  # a set of absolute paths
    for path in data['batch']:
        datum = fs.load(path)
        files.update(datum.values())
    for path in data['single']:
        if path.endswith('/'):
            dirs.add(fs.abspath(path))
        else:
            files.add(fs.abspath(path))
    
    abspath_dirs = set()
    for f in files:
        abspath_dirs.add(fs.parent(f))
    for d in dirs:
        abspath_dirs.add(d)
    # noinspection PyTypeChecker
    base_prefix: str = fs.normpath(os.path.commonpath(abspath_dirs))
    print(base_prefix, len(abspath_dirs), len(files), ':v2l')
    assert base_prefix.startswith(p('../../'))
    
    relpath_dirs = (x.removeprefix(base_prefix + '/') for x in abspath_dirs)
    init_target_tree(dir_o, relpath_dirs)
    
    for f in files:
        i = f
        o = '{}/{}'.format(dir_o, f.removeprefix(base_prefix + '/'))
        fs.copy_file(i, o)
    for d in dirs:
        i = d
        o = '{}/{}'.format(dir_o, d.removeprefix(base_prefix + '/'))
        fs.copy_tree(i, o, True)
    
    print('done', ':t')
