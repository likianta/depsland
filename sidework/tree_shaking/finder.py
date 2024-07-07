if __name__ == '__main__':
    __package__ = 'sidework.tree_shaking'

import typing as t

from argsense import cli

from lk_utils import fs
from lk_utils import p
from .file_parser import FileParser
from .file_parser import T


@cli.cmd()
def dump_all_references(entrances: str) -> None:
    d0 = find_all_references(*entrances.split(",,"))
    d1 = {}
    for module in sorted(d0.keys()):
        print(module, ":iv2s")
        d1[module] = d0[module]
    fs.dump(d1, p("_references.yaml"))
    print(":t", 'done. see result at "_references.yaml"')


def find_all_references(*entrance_scripts: str) -> t.Dict[T.ModuleName, T.Path]:
    """
    warning: this is time-consuming.
    """
    out = {}
    for script in map(fs.abspath, entrance_scripts):
        out.update(get_all_imports(script))
    return out


def get_all_imports(script: T.Path, _holder: t.Set = None) -> T.ImportsInfo:
    if _holder is None:
        _holder = set()
    for module, path in get_direct_imports(script):
        print(module, path)
        if module not in _holder:
            _holder.add(module)
            yield module, path
            if path.endswith('.py'):
                yield from get_all_imports(path, _holder)


def get_direct_imports(script: T.Path) -> T.ImportsInfo:
    parser = FileParser(script)
    return parser.parse_imports()


if __name__ == "__main__":
    # pox sidework/tree_shaking/finder.py dump-all-references
    #   depsland/__init__.py,,depsland/__main__.py
    cli.run()
