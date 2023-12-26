import re
import sys
import typing as t

from lk_utils import fs
from lk_utils import loads
from lk_utils import run_cmd_args

from ...normalization import normalize_name

_poetry = (sys.executable, '-m', 'poetry')


class T:
    Format = t.Literal[
        'auto',
        'pyproject.toml',
        'requirements.txt',
        # TODO: 'poetry.lock', 'pipfile.lock', 'requirements.lock', \
        #   'requirements.yaml'.
    ]
    LibraryPath = str
    PackageName = str


# -----------------------------------------------------------------------------


def get_library_root(working_root: str) -> T.LibraryPath:
    from ...platform.system_info import IS_WINDOWS
    venv_root = fs.normpath(
        run_cmd_args(
            (*_poetry, 'env', 'info'),
            ('--path', '--no-ansi'),
            ('--directory', working_root),
        )
    )
    if IS_WINDOWS:
        out = '{}/Lib/site-packages'.format(venv_root)
    else:
        out = '{}/lib/python{}.{}/site-packages'.format(
            venv_root, sys.version_info.major, sys.version_info.minor
        )
    assert fs.exists(out)
    return out


def get_top_package_names(
    file: str, format: T.Format = 'auto'
) -> t.Iterator[T.PackageName]:
    """
    NOTE: be sure the yielded result is normalized by `normalize_name`.
    """
    if format == 'auto':
        format = (
            'pyproject.toml'
            if file.endswith('pyproject.toml')
            else 'requirements.txt'
        )
    assert file.endswith(('.toml', '.txt'))
    assert format in ('pyproject.toml', 'requirements.txt')
    print(file, format)
    if format == 'pyproject.toml':
        # yield from _get_top_names_by_poetry_2(working_root=fs.parent(file))
        yield from _get_top_names_by_poetry_3(file)
    else:
        yield from _get_top_names_from_requirements_file(file)


def get_top_package_names_by_poetry(
    working_root: str,
) -> t.Iterator[T.PackageName]:
    yield from _get_top_names_by_poetry_2(working_root)


# -----------------------------------------------------------------------------


def _get_top_names_by_poetry_1(working_root: str) -> t.Iterator[T.PackageName]:
    # FIXME: there is a bug (?) that it may not show all top names if some \
    #   packages have custom urls. please use `_get_top_names_by_poetry_2` as \
    #   a workaround.
    yield from map(
        normalize_name,
        run_cmd_args(
            _poetry,
            ('show', '-T', '--no-ansi'),
            ('--directory', working_root),
        ).splitlines(),
    )


def _get_top_names_by_poetry_2(working_root: str) -> t.Iterator[T.PackageName]:
    content = run_cmd_args(
        _poetry,
        ('show', '-t', '--no-dev', '--no-ansi'),
        ('--directory', working_root),
    )
    re_pkg_name = re.compile(r'^[-\w]+')
    for line in content.splitlines():
        if line.startswith((' ', '│', '├', '└')):
            continue
        # print(':vi2', line, bool(re_pkg_name.match(line)))
        if m := re_pkg_name.match(line):
            yield normalize_name(m.group())


def _get_top_names_by_poetry_3(toml_file: str) -> t.Iterator[T.PackageName]:
    """
    parse pyproject.toml and get the names.
    this may not a good idea. use `_get_top_names_by_poetry_2` instead.
    """
    if sys.version_info >= (3, 11):
        from tomllib import load
    else:  # pip install toml
        from toml import load  # noqa
    with open(toml_file, 'rb') as f:
        data: dict = load(f)
    deps: dict = data['tool']['poetry']['dependencies']
    deps.pop('python')
    for k, group in data['tool']['poetry']['group'].items():
        # TODO: skip values if its restrictions not match current version.
        if k != 'dev':
            deps.update(group['dependencies'])
    print(deps, ':l')
    return map(normalize_name, deps.keys())


def _get_top_names_from_requirements_file(
    reqs_file: str,
) -> t.Iterator[T.PackageName]:
    re_name = re.compile(r'^ *([-\w]+)', re.M)
    yield from map(normalize_name, re_name.findall(loads(reqs_file)))
