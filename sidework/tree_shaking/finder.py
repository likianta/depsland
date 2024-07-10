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
    missing_files = _postfix_missing_init_files(out.values())
    i = 0
    for i, f in enumerate(sorted(missing_files), 1):
        out['__auto_import_{}'.format(i)] = f
    if i:
        print('postfix {} init files'.format(i))
    return out


def get_all_imports(
    script: T.Path, _holder: t.Set = None
) -> t.Iterator[t.Tuple[T.ModuleName, T.Path]]:
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


def _postfix_missing_init_files(all_paths: t.Iterable[str]) -> t.Iterator[str]:
    all_paths = set(all_paths)
    found = set(
        x.rsplit('/', 1)[0]
        for x in all_paths
        if x.endswith('/__init__.py')
    )
    for f in all_paths:
        if not f.endswith('__init__.py'):
            d = f.rsplit('/', 1)[0]
            if d not in found:
                if fs.exists(x := f'{d}/__init__.py'):
                    yield x
