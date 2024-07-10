import ast
import atexit
import typing as t

from lk_utils import fs
from lk_utils import p


class FileNodesCache:
    
    def __init__(self, pkl_file: str) -> None:
        self._file = pkl_file
        self._cache = fs.load(pkl_file)
        self._changed = False
        atexit.register(self._save)
    
    def parse_nodes(
        self, file: str
    ) -> t.Iterator[t.Tuple[t.Union[ast.Import, ast.ImportFrom], str]]:
        if file in self._cache:
            yield from self._cache[file]
            return
        print(':i2', 'parsing file', file)
        source = fs.load(file, 'plain')
        lines = source.splitlines()
        tree = ast.parse(source, file)
        nodes = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                line = lines[node.lineno - 1]
                yield node, line
                nodes.append((node, line))
        self._cache[file] = tuple(nodes)
        self._changed = True
    
    def _save(self) -> None:
        if self._changed:
            fs.dump(self._cache, self._file)


if not fs.exists(x := p('_file_nodes_cache.pkl')):
    fs.dump({}, x)
file_cache = FileNodesCache(x)
