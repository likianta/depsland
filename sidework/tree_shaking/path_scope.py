from lk_utils import fs
from lk_utils import p


class T:
    Anypath = str
    Dirpath = str


class PathScope:
    
    def __init__(self) -> None:
        self.module_2_path = {}
        self.path_2_module = {}
        self.add_scope('.')
    
    def add_scope(self, scope: T.Dirpath) -> None:
        module_2_path = {}
        path_2_module = {}
        scope = fs.abspath(scope)
        for d in fs.find_dirs(scope, filter=True):
            if '.' not in d.name:
                module_2_path[d.name] = (d.path, True)
                path_2_module[d.path] = d.name
        for f in fs.find_files(scope, ('.py', '.pyc', '.pyd'), filter=True):
            module_2_path[f.stem] = (f.path, False)
            path_2_module[f.path] = f.stem
        self.module_2_path.update(module_2_path)
        self.path_2_module.update(path_2_module)
        # sort paths from long to short
        self.path_2_module = dict(sorted(
            self.path_2_module.items(),
            key=lambda x: x[0],
            reverse=True
        ))
    
    def add_path(self, path: T.Anypath) -> None:
        path = fs.abspath(path)
        self.module_2_path[x := fs.barename(path)] = (path, fs.isdir(path))
        self.path_2_module[path] = x
        # sort paths from long to short
        self.path_2_module = dict(sorted(
            self.path_2_module.items(),
            key=lambda x: x[0],
            reverse=True
        ))


path_scope = PathScope()
path_scope.add_scope(p('../../chore/site_packages'))
path_scope.add_path(p('../../depsland'))
