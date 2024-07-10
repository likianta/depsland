import typing as t

from depsland.utils.fs import get_content_hash
from lk_utils import fs
from lk_utils import p
from .file_parser import FileParser
from .file_parser import T


def get_result_file(script: str) -> str:
    return p('results/{}-{}.yaml'.format(
        fs.barename(script), get_content_hash(fs.abspath(script))[::4]
    ))


def dump_all_imports(
    script: T.Path, result_file: str = None, sort: bool = False
) -> t.Tuple[t.Dict[T.ModuleName, T.Path], T.Path]:
    result = dict(get_all_imports(script))
    if sort:
        result = dict(sorted(result.items()))
    # for module in result:
    #     print(':i', module)
    if not result_file:
        result_file = get_result_file(script)
    fs.dump(result, result_file)
    return result, result_file


def get_all_imports(
    script: T.Path,
    _resolved_modules: t.Set = None,
    _resolved_init_files: t.Set = None,
) -> t.Iterator[t.Tuple[T.ModuleName, T.Path]]:
    """
    given a script file ('*.py'), return all direct and indirect modules that
    are imported by this file.
    """
    if _resolved_modules is None:
        _resolved_modules = set()
        _resolved_init_files = set()
    for module, path in get_direct_imports(script):
        # print(module, path)
        assert module.full_name
        if module.full_name not in _resolved_modules:
            _resolved_modules.add(module.full_name)
            yield module.full_name, path
            if path.endswith('.py'):  # to deviate '.pyc' and '.pyd' files
                yield from get_all_imports(
                    path,
                    _resolved_modules,
                    _resolved_init_files,
                )
            
            if path.endswith('/__init__.py'):
                _resolved_init_files.add(path)
            else:
                possible_init_file = '{}/__init__.py'.format(
                    path.rsplit('/', 1)[0]
                )
                if possible_init_file not in _resolved_init_files:
                    _resolved_init_files.add(possible_init_file)
                    if fs.exists(possible_init_file):
                        global _auto_index
                        _auto_index += 1
                        yield (
                            '__implicit_import_{}'.format(_auto_index),
                            possible_init_file
                        )
                        yield from get_all_imports(
                            possible_init_file,
                            _resolved_modules,
                            _resolved_init_files,
                        )


_auto_index = 0


def get_direct_imports(script: T.Path) -> T.ImportsInfo:
    parser = FileParser(script)
    return parser.parse_imports()
