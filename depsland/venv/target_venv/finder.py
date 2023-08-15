import os
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
    venv_root = fs.normpath(
        run_cmd_args(
            _poetry, 'env', 'info', '--path', '-C', working_root
        )
    )
    if os.name == 'nt':
        out = f'{venv_root}/Lib/site-packages'
    else:
        out = '{}/lib/python{}.{}/site-packages'.format(
            venv_root, sys.version_info.major, sys.version_info.minor
        )
    assert fs.exists(out)
    return out


def get_top_package_names(
    file: str, format: T.Format = 'auto'
) -> t.Iterator[T.PackageName]:
    if format == 'auto':
        format = (
            'pyproject'
            if file.endswith('pyproject.toml')
            else 'requirements.txt'
        )
    if format == 'pyproject.toml':
        yield from _get_top_names_by_poetry_2(working_root=fs.parent(file))
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
            ('show', '-T'),
            ('--directory', working_root),
        ).splitlines(),
    )


def _get_top_names_by_poetry_2(working_root: str) -> t.Iterator[T.PackageName]:
    content = run_cmd_args(
        _poetry,
        ('show', '-t', '--no-dev'),
        ('--directory', working_root),
    )
    re_pkg_name = re.compile(r'^[-\w]+')
    for line in content.splitlines():
        if m := re_pkg_name.match(line):
            yield normalize_name(m.group())


# noinspection PyUnusedLocal
def _get_top_names_by_poetry_3(toml_file: str) -> t.Iterator[T.PackageName]:
    """
    parse pyproject.toml and get the names.
    this may not a good idea. use `_get_top_names_by_poetry_2` instead.
    """
    raise NotImplementedError


def _get_top_names_from_requirements_file(
    reqs_file: str,
) -> t.Iterator[T.PackageName]:
    re_name = re.compile(r'^ *([-\w]+)', re.M)
    yield from map(normalize_name, re_name.findall(loads(reqs_file)))
