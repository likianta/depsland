"""
a wrapper for pip command.
"""
import re
import typing as t

from lk_utils.filesniff import normpath
from lk_utils.subproc import compose_cmd
from lk_utils.subproc import run_cmd_args
from yaml import safe_load as yaml_safe_load

from . import paths
from .config import app_settings


class T:
    PipCommand = t.Tuple[str, ...]  # e.g. ('python3', '-m', 'pip')
    PopenArgs = t.Iterable[str]


class Pip:
    _pip_exec: T.PipCommand
    _template: 'CommandTemplate'
    
    def __init__(
            self,
            pip_cmd: T.PipCommand,
            pip_conf=app_settings['pip'],
            local=paths.pypi.downloads,
    ):
        self._pip_exec = pip_cmd
        self._template = CommandTemplate(pip_cmd, local, **pip_conf)
    
    def update_pip_options(self, **options):
        # noinspection PyArgumentList
        self._template = CommandTemplate(self._pip_exec, **options)
    
    def run(self, *args: t.Union[str, t.Tuple[str, ...]]) -> str:
        args = compose_cmd(*args)
        return self._run(*self._pip_exec, *args)
    
    @staticmethod
    def _run(*args: str) -> str:
        """
        both print and return the command line output.
        """
        print(':r', '[magenta dim]{}[/]'
              .format(' '.join(args).replace('[', '\\[')))
        return run_cmd_args(*args, verbose=True, ignore_error=False)
    
    # -------------------------------------------------------------------------
    
    def test(self) -> None:
        self._run(*self._pip_exec, '--version')
    
    def pip_version(self) -> str:
        r = self._run(*self._pip_exec, '--version')
        return r.split(' ', 2)[1]
        #   ['pip', '22.3', 'from ...'] -> '22.3'
    
    def download(
            self, name: str, version='',
            dest=paths.pypi.downloads, no_deps=False
    ) -> str:
        return self._run(
            *self._template.pip_download(name, version, dest, no_deps)
        )
    
    def download_r(self, file: str, dest=paths.pypi.downloads) -> str:
        return self._run(*self._template.pip_download_r(file, dest))
    
    def install(
            self, name: str, version='',
            dest=paths.pypi.installed, no_deps=False
    ) -> str:
        return self._run(
            *self._template.pip_install(name, version, dest, no_deps)
        )
    
    def install_r(self, file: str, dest=paths.pypi.installed) -> str:
        return self._run(*self._template.pip_install_r(file, dest))
    
    # -------------------------------------------------------------------------
    
    def show_dependencies(self, name: str) -> t.List[str]:
        resp = self._run(*self._template.pip_show(name))
        #   it can be considered as a YAML string.
        data: dict = yaml_safe_load(resp)
        if data['Requires']:
            return data['Requires'].split(', ')
            #   e.g. {'Requires': 'xlrd, lk-logger, xlsxwriter', ...} ->
            #       ['xlrd', 'lk-logger', 'xlsxwriter']
        else:
            return []
    
    def show_locations(self, name: str) -> t.Set[str]:
        resp = self._run(*self._template.pip_show_f(name))
        r''' e.g.
            Name: lk-logger
            Version: 3.6.3
            Summary: Advanced logger with source code lineno indicator.
            Home-page:
            Author: Likianta
            Author-email: likianta@foxmail.com
            License: MIT
            Location: e:\programs\python\python39\lib\site-packages
            Requires:
            Required-by: pyportable-installer, lk-utils, lk-qtquick-scaffold
            Files:
              lk_logger-3.6.3.dist-info\INSTALLER
              lk_logger-3.6.3.dist-info\METADATA
              lk_logger-3.6.3.dist-info\RECORD
              lk_logger-3.6.3.dist-info\REQUESTED
              lk_logger-3.6.3.dist-info\WHEEL
              lk_logger\__init__.py
              lk_logger\__pycache__\__init__.cpython-39.pyc
              lk_logger\__pycache__\lk_logger.cpython-39.pyc
              lk_logger\lk_logger.py
        '''
        resp = resp.replace('  ', '  - ')
        data: dict = yaml_safe_load(resp)
        #   {'Name': 'lk-logger', ... 'Files': [...]}
        
        # analyse files root dirs
        out = set()
        for f in data['Files'].split('\n'):
            if f == '':
                continue
            if f.startswith('.'):
                #   e.g. '..\..\Scripts\vba_extract.py'
                assert f.startswith('..\\..\\Scripts\\')
                out.add('../../Scripts/{}'.format(
                    normpath(f[14:]).split('/', 1)[0]
                ))
            else:
                out.add(normpath(f).split('/', 1)[0])
        return out


class CommandTemplate:
    
    def __init__(
            self,
            pip_cmd: T.PipCommand,
            local_dir: str = paths.pypi.downloads,
            cache_dir: str = paths.pypi.cache,
            *,
            index_url: str = 'https://pypi.python.org/simple/',
            local_first: bool = False,
            offline: bool = False,
            quiet: bool = False,
            **_,
    ):
        # extend parameters
        if offline:
            host = ''
            local_first = True
        else:
            assert index_url
            host = re.search(r'https?://([^/]+)', index_url).group(1)
        # if local_first:
        #     url_indexes = (local_dir, index_url)
        # else:
        #     url_indexes = (index_url, local_dir)
        
        self._pip = pip_cmd
        
        self._pip_options = tuple(compose_cmd(
            f'--cache-dir', cache_dir,
            f'--disable-pip-version-check',
            f'--no-python-version-warning',
            f'--quiet' if quiet else '',
            ('--trusted-host', host)
        ))
        self._pip_options_2 = tuple(compose_cmd(
            f'--disable-pip-version-check',
            f'--quiet' if quiet else '',
        ))
        
        self._pip_download_options = tuple(compose_cmd(
            f'--no-index' if offline else '',
            # f'--only-binary=:all:',
            ('--find-links', local_dir),
            ('--index-url', index_url),
            # ('--index-url', url_indexes[0]),
            # ('--extra-index-url', url_indexes[1]),
        ))
        self._pip_install_options = (
            *self._pip_download_options,
            '--no-warn-script-location',
        )
    
    # -------------------------------------------------------------------------
    
    def pip_download(
            self, name: str, version='', dest='', no_deps=False
    ) -> T.PopenArgs:
        return compose_cmd(
            *self._pip, 'download', f'{name}{version}'.replace(' ', ''),
            ('-d', dest), ('--no-deps' if no_deps else ''),
            *self._pip_options, *self._pip_download_options
        )
    
    def pip_download_r(self, file: str, dest: str = '') -> T.PopenArgs:
        return compose_cmd(
            *self._pip, 'download', '-r', file, ('-d', dest),
            *self._pip_options, *self._pip_download_options
        )
    
    def pip_install(
            self, name: str, version='', dest='', no_deps=False
    ) -> T.PopenArgs:
        return compose_cmd(
            *self._pip, 'install', f'{name}{version}'.replace(' ', ''),
            ('-t', dest), ('--no-deps' if no_deps else ''),
            *self._pip_options, *self._pip_install_options
        )
    
    def pip_install_r(self, file: str, dest: str = '') -> T.PopenArgs:
        return compose_cmd(
            *self._pip, 'install', '-r', file, ('-t', dest),
            *self._pip_options, *self._pip_install_options
        )
    
    def pip_show(self, name: str) -> T.PopenArgs:
        return compose_cmd(
            *self._pip, 'show', name,
            *self._pip_options_2
        )
    
    def pip_show_f(self, name: str) -> T.PopenArgs:
        return compose_cmd(
            *self._pip, 'show', name, '-f',
            *self._pip_options_2
        )


pip = Pip(
    pip_cmd=(paths.python.python, '-m', 'pip'),
    local=paths.pypi.downloads,
)
