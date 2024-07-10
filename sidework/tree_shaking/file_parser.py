import ast
import atexit
import typing as t
from contextlib import contextmanager

from lk_logger import parallel_printing
from lk_utils import fs
from lk_utils import p
from .cache import file_cache
from .module import ModuleInfo
from .module import ModuleInspector
from .module import ModuleNotFound
from .module import PathNotFound
from .module import T as T0
from .path_scope import path_scope

module_inspector = ModuleInspector(
    ignores=fs.load(p('./_ignores.txt')).splitlines()
)
_broken = set()


class T(T0):
    ImportsInfo = t.Iterator[t.Tuple[T0.ModuleInfo, T0.Path]]
    #   ((module_info, path), ...)
    #       module_info: dataclass ModuleInfo
    Node = t.Union[ast.Import, ast.ImportFrom]


# noinspection PyMethodMayBeStatic
class FileParser:
    
    def __init__(self, file: T.Path) -> None:
        self.file = file
        self.dir = fs.parent(file)
        
        if self.file in path_scope.path_2_module:
            self.base_dir = self.dir
            self.base_module_segs = ()
        elif self.dir in path_scope.path_2_module:
            self.base_dir = self.dir
            self.base_module_segs = (path_scope.path_2_module[self.dir],)
        else:
            for top_path, top_name in path_scope.path_2_module.items():
                if self.file.startswith(top_path + '/'):
                    self.base_dir = top_path
                    self.base_module_segs = (
                        top_name, *self.dir[len(top_path) + 1:].split('/')
                    )
                    break
            else:
                raise Exception(
                    'file should be existed in registered path scopes', file
                )
    
    def parse_imports(self) -> T.ImportsInfo:
        # print(':dv2sp', 'start', self.file)
        for node, line in file_cache.parse_nodes(self.file):
            for module in self._get_module_info(node, line):
                try:
                    path = self._get_module_path(module)
                except (ModuleNotFound, PathNotFound) as e:
                    if module.id not in _broken:
                        _broken.add(module.id)
                        with _err_records.recording():
                            # print(
                            #     ':v3l',
                            #     '{}:{}'.format(self.file, node.lineno),
                            #     line.strip(),
                            #     module,
                            #     type(e),
                            # )
                            pass
                    continue
                except Exception as e:
                    print(':v4l', self.file, node.lineno, module)
                    raise e
                if path in ('<stdlib>', '<ignored>'):
                    continue
                else:
                    yield module, path
        # print(':vsp', 'end', self.file)
    
    def _check_if_relative_import(self, line: str) -> int:
        x = line.lstrip().split()[1]
        if not x: raise Exception('empty import', self.file, line)
        dot_cnt = 0
        for ch in x:
            if ch == '.':
                dot_cnt += 1
            else:
                break
        return dot_cnt
    
    def _get_module_info(
        self, node: T.Node, line: str
    ) -> t.Iterator[T.ModuleInfo]:
        if dot_cnt := self._check_if_relative_import(line):
            if dot_cnt == 1:
                base_module = '.'.join(self.base_module_segs)
            else:
                base_module = '.'.join(self.base_module_segs[:-(dot_cnt - 1)])
        else:
            base_module = None
        if base_module:
            base_dir = fs.normpath(
                '{}/{}'.format(self.dir, '../' * (dot_cnt - 1))
            )
        else:
            base_dir = None
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                if base_module:
                    module_name = '{}.{}'.format(base_module, alias.name)
                else:
                    module_name = alias.name
                yield ModuleInfo(
                    name0=module_name,
                    name1=alias.name,
                    name2='',
                    level=dot_cnt,
                    base_dir=base_dir,
                )
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
                yield ModuleInfo(
                    name0=module_name,
                    name1=node.module or '',
                    name2=alias.name,
                    level=dot_cnt,
                    base_dir=base_dir,
                )
    
    def _get_module_path(self, module: T.ModuleInfo) -> T.Path:
        # assert '//' not in module_inspector.find_module_path(module), module
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
