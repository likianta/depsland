import typing as t

from lk_utils import fs
from .file_parser import FileParser
from .file_parser import T


def find_all_references(*entrance_scripts: str) -> t.Dict[T.ModuleId, T.Path]:
    """
    warning: this is time-consuming.
    """
    out = {}
    for script in map(fs.abspath, entrance_scripts):
        out.update(get_all_imports(script))
    return out


def get_all_imports(
    script: T.Path, _holder: t.Set = None
) -> t.Iterator[t.Tuple[T.ModuleId, T.Path]]:
    if _holder is None:
        _holder = set()
    for module, path in get_direct_imports(script):
        # print(module, path)
        assert module.full_name
        if module.full_name not in _holder:
            _holder.add(module.full_name)
            yield module.full_name, path
            if path.endswith('.py'):
                yield from get_all_imports(path, _holder)


def get_direct_imports(script: T.Path) -> T.ImportsInfo:
    parser = FileParser(script)
    return parser.parse_imports()
