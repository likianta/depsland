import ast
import typing as t

from lk_utils import fs
from lk_utils import p
from .module import ModuleInspector, PathNotFound
from .module import T as T0

module_inspector = ModuleInspector(
    search_scopes=(p('../../chore/site_packages'),),
    search_paths=(p('../../depsland'),)
)


class T(T0):
    ImportsInfo = t.Iterator[t.Tuple[T0.ModuleName, T0.Path]]


class FileParser:
    
    def __init__(self, file: T.Path) -> None:
        self.file = file
        self.dir = fs.parent(file)
        self.code = fs.load(file)
        self.lines = tuple(self.code.splitlines())
    
    def parse_imports(self) -> T.ImportsInfo:
        print(':dvsp', 'start', self.file)
        tree = ast.parse(self.code, self.file)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for module_name in self._get_module_name(node):
                    print(module_name, node.lineno, ':i')
                    if module_name.startswith('lk_utils'):  # TEST
                        print(module_name, self._get_path(
                            module_name, node.lineno
                        ))
                        if input('continue: ') == 'x':
                            import sys
                            sys.exit()
                    try:
                        path = self._get_path(module_name, node.lineno)
                    except PathNotFound as e:
                        print(
                            ':v3l',
                            'module not found',
                            '{}:{}'.format(self.file, node.lineno),
                            self.lines[node.lineno - 1].strip(),
                            e.args,
                        )
                        continue
                    except Exception as e:
                        print(':v4l', self.file, node.lineno, module_name)
                        raise e
                    if path != '<stdlib>':
                        yield module_name, path
        print(':vsp', 'end', self.file)
    
    def _get_module_name(self, node: ast.AST) -> t.Iterator[T.ModuleName]:
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if node.module is None:
                    yield alias.name
                else:
                    yield '{}.{}'.format(node.module, alias.name)
    
    def _get_path(self, module: T.ModuleName, lineno: int) -> T.Path:
        line: str = self.lines[lineno - 1]
        if line.split()[1].startswith('.'):
            # relative import
            path = fs.normpath('{}/{}'.format(
                self.dir, '../' * (line.count('.') - 1)
            ))
            return module_inspector.get_module_path(module, path)
        else:
            return module_inspector.get_module_path(module)
