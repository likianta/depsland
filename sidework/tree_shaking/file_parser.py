import ast
import atexit
import typing as t
from contextlib import contextmanager

from lk_logger import parallel_printing
from lk_utils import fs
from lk_utils import p
from .module import ModuleInspector, ModuleNotFound
from .module import PathNotFound, ModuleInfo
from .module import T as T0

module_inspector = ModuleInspector(
    search_scopes=(p('../../chore/site_packages'),),
    search_paths=(p('../../depsland'),),
    ignores=frozenset(fs.load(p('./_ignores.txt')).splitlines())
)
_broken = set()


class T(T0):
    ImportsInfo = t.Iterator[t.Tuple[T0.ModuleInfo, T0.Path]]
    Node = t.Union[ast.Import, ast.ImportFrom]


# noinspection PyMethodMayBeStatic
class FileParser:
    
    def __init__(self, file: T.Path) -> None:
        self.file = file
        self.dir = fs.parent(file)
        self.code = fs.load(file)
        self.lines = tuple(self.code.splitlines())
    
    def parse_imports(self) -> T.ImportsInfo:
        print(':dv2sp', 'start', self.file)
        tree = ast.parse(self.code, self.file)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for module in self._get_module_info(node):
                    # print(module, node.lineno, ':i')
                    # if module.name.startswith('lk_utils'):  # TEST
                    #     print(module.name, self._get_path(
                    #         module.name, node.lineno
                    #     ))
                    #     if input('continue: ') == 'x':
                    #         import sys
                    #         sys.exit()
                    try:
                        path = self._get_module_path(module)
                    except (ModuleNotFound, PathNotFound) as e:
                        if module.id not in _broken:
                            _broken.add(module.id)
                            with _err_records.recording():
                                print(
                                    ':v3l',
                                    '{}:{}'.format(self.file, node.lineno),
                                    self.lines[node.lineno - 1].strip(),
                                    module,
                                    type(e),
                                )
                        continue
                    except Exception as e:
                        print(':v4l', self.file, node.lineno, module)
                        raise e
                    if path in ('<stdlib>', '<ignored>'):
                        continue
                    else:
                        yield module, path
        print(':vsp', 'end', self.file)
    
    def _check_if_relative_import(self, node: ast.AST) -> int:
        lineno = node.lineno
        line = self.lines[lineno - 1]
        x = line.split()[1]
        if not x: raise Exception('empty import', self.file, lineno, line)
        dot_cnt = 0
        for ch in x:
            if ch == '.':
                dot_cnt += 1
            else:
                break
        return dot_cnt
    
    def _get_module_info(self, node: T.Node) -> t.Iterator[T.ModuleInfo]:
        if dot_cnt := self._check_if_relative_import(node):
            base_module = '.'.join(self.dir.rsplit('/', dot_cnt)[1:])
            assert base_module.count('.') == dot_cnt - 1
        else:
            base_module = None
        if base_module:
            base_dir = fs.normpath('{}/{}'.format(
                self.dir, '../' * (dot_cnt - 1)
            ))
        else:
            base_dir = None
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                if base_module:
                    module_name = '{}.{}'.format(base_module, alias.name)
                else:
                    module_name = alias.name
                yield ModuleInfo(module_name, '', dot_cnt, base_dir)
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if base_module:
                    if node.module:
                        module_name = '{}.{}'.format(base_module, node.module)
                    else:
                        module_name = base_module
                else:
                    if node.module:
                        module_name = node.module
                    else:
                        raise Exception
                yield ModuleInfo(module_name, alias.name, dot_cnt, base_dir)
    
    def _get_module_path(self, module: T.ModuleInfo) -> T.Path:
        return module_inspector.find_module_path(module)


class ErrorRecords:
    
    def __init__(self) -> None:
        self._records = []
        atexit.register(self.save)
    
    @contextmanager
    def recording(self) -> t.Iterator:
        with parallel_printing(self._log):
            yield
    
    def _log(self, msg: str) -> None:
        self._records.append(str(msg))
    
    def save(self) -> bool:
        if self._records:
            fs.dump(self._records, p('_errors.txt'))
            print(
                'found {} errors. see log at "_errors.txt"'
                .format(len(self._records)), ':v4s'
            )
            return True
        return False


_err_records = ErrorRecords()
