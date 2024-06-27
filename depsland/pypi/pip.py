"""
a wrapper for pip command.
"""
import sys
import typing as t

from lk_utils.subproc import run_cmd_args

from .. import paths
from ..config import app_settings


class T:
    PipExecute = t.Tuple[str, ...]  # e.g. ('python3', '-m', 'pip')
    PopenArg = t.Union[str, t.Tuple[str, ...]]


class Pip:
    _pip_exec: T.PipExecute
    _pip_general_options: t.Tuple[T.PopenArg, ...]
    
    def __init__(
        self,
        pip_exec: T.PipExecute = (sys.executable, '-m', 'pip'),
        *,
        # download_dir: str = paths.pypi.downloads,
        index_url: str = 'https://pypi.python.org/simple/',
    ) -> None:
        self._pip_exec = pip_exec
        self._pip_general_options = (
            '--disable-pip-version-check',
            '--no-python-version-warning',
            ('--find-links', paths.pypi.downloads),
            ('--index-url', index_url),
            ('--trusted-host', index_url.split('/')[2]),
        )
    
    def pip_cmd(self, *args: T.PopenArg) -> str:
        return run_cmd_args(
            *self._pip_exec, *args,
            verbose=True, ignore_error=False
        )
    
    def test(self) -> None:
        self.pip_cmd('--version')
    
    def pip_version(self) -> str:
        r = self.pip_cmd('--version')
        return r.split(' ', 2)[1]  # ['pip', '22.3', 'from ...'] -> '22.3'
    
    # -------------------------------------------------------------------------
    
    def download(
        self,
        name: str,
        destination: str = paths.pypi.downloads,
        no_dependency: bool = False,
        no_index: bool = False,
    ) -> str:
        """
        params:
            name: support the following formats:
                '<package_name>'
                '<package_name><comparator><version>'
                '<url>'
            no_index:
                carefully setting this True. if no_index is True, the packages -
                which requires setuptools etc. will be failed to build local -
                wheels.
                see also https://github.com/pypa/pip/issues/12050
        """
        return self.pip_cmd(
            ('wheel', name),
            ('-w', destination),
            '--no-deps' if no_dependency else '',
            '--no-index' if no_index else '',
            *self._pip_general_options,
        )
    
    def download_r(
        self,
        file: str,
        destination: str = paths.pypi.downloads,
        no_dependency: bool = False,
        no_index: bool = False,
    ) -> str:
        return self.pip_cmd(
            ('wheel', '-r', file),
            ('-w', destination),
            '--no-deps' if no_dependency else '',
            '--no-index' if no_index else '',
            *self._pip_general_options,
        )
    
    def install(
        self,
        name: str,
        destination: str,
        no_dependency: bool = False,
        no_index: bool = False,
    ) -> str:
        return self.pip_cmd(
            ('install', name),
            ('-t', destination),
            '--no-deps' if no_dependency else '',
            '--no-index' if no_index else '',
            *self._pip_general_options,
            '--no-warn-script-location',
        )
    
    def install_r(
        self,
        file: str,
        destination: str,
        no_dependency: bool = False,
        no_index: bool = False,
    ) -> str:
        return self.pip_cmd(
            ('install', '-r', file),
            ('-t', destination),
            '--no-deps' if no_dependency else '',
            '--no-index' if no_index else '',
            *self._pip_general_options,
            '--no-warn-script-location',
        )
    
    # -------------------------------------------------------------------------
    
    # def show_dependencies(self, name: str) -> t.List[str]:
    #     resp = self._run(*self._template.pip_show(name))
    #     #   it can be considered as a YAML string.
    #     data: dict = yaml_safe_load(resp)
    #     if data['Requires']:
    #         return data['Requires'].split(', ')
    #         #   e.g. {'Requires': 'xlrd, lk-logger, xlsxwriter', ...} ->
    #         #       ['xlrd', 'lk-logger', 'xlsxwriter']
    #     else:
    #         return []
    #
    # def show_locations(self, name: str) -> t.Set[str]:
    #     resp = self._run(*self._template.pip_show_f(name))
    #     r''' e.g.
    #         Name: lk-logger
    #         Version: 3.6.3
    #         Summary: Advanced logger with source code lineno indicator.
    #         Home-page:
    #         Author: Likianta
    #         Author-email: likianta@foxmail.com
    #         License: MIT
    #         Location: e:\programs\python\python39\lib\site-packages
    #         Requires:
    #         Required-by: pyportable-installer, lk-utils, lk-qtquick-scaffold
    #         Files:
    #           lk_logger-3.6.3.dist-info\INSTALLER
    #           lk_logger-3.6.3.dist-info\METADATA
    #           lk_logger-3.6.3.dist-info\RECORD
    #           lk_logger-3.6.3.dist-info\REQUESTED
    #           lk_logger-3.6.3.dist-info\WHEEL
    #           lk_logger\__init__.py
    #           lk_logger\__pycache__\__init__.cpython-39.pyc
    #           lk_logger\__pycache__\lk_logger.cpython-39.pyc
    #           lk_logger\lk_logger.py
    #     '''
    #     resp = resp.replace('  ', '  - ')
    #     data: dict = yaml_safe_load(resp)
    #     #   {'Name': 'lk-logger', ... 'Files': [...]}
    #
    #     # analyse files root dirs
    #     out = set()
    #     for f in data['Files'].split('\n'):
    #         if f == '':
    #             continue
    #         if f.startswith('.'):
    #             #   e.g. '..\..\Scripts\vba_extract.py'
    #             assert f.startswith('..\\..\\Scripts\\')
    #             out.add('../../Scripts/{}'.format(
    #                 normpath(f[14:]).split('/', 1)[0]
    #             ))
    #         else:
    #             out.add(normpath(f).split('/', 1)[0])
    #     return out


pip = Pip(
    pip_exec=(paths.python.python, '-m', 'pip'),
    index_url=app_settings['pip']['index_url']
)
