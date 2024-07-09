import ast
import re
import sys
import typing as t
from dataclasses import dataclass
from functools import cached_property

from lk_utils import fs


@dataclass
class ModuleInfo:
    name: str
    end: str
    level: int
    base_dir: t.Optional[str]
    
    def __str__(self) -> str:
        return self.id
    
    @cached_property
    def relname(self) -> str:
        if self.level:
            return '.'.join(self.name.split('.')[self.level:])
        return self.name
    
    @cached_property
    def id(self) -> str:
        return '{}.{}'.format(self.name, self.end).rstrip('.')
    
    @cached_property
    def top(self) -> str:
        return self.name.split('.', 1)[0]


class T:
    ModuleId = str
    ModuleInfo = ModuleInfo
    ModuleName = str
    Path = str  # normalized absolute path


# noinspection PyMethodMayBeStatic
class ModuleInspector:
    ignores: t.FrozenSet[str]
    known_stdlib_module_names: t.FrozenSet[str]
    module_name_2_file: t.Dict[T.ModuleId, T.Path]
    top_name_2_path: t.Dict[T.ModuleName, t.Tuple[T.Path, bool]]
    
    def __init__(
        self,
        search_scopes: t.Iterable[str] = None,
        search_paths: t.Iterable[str] = (),
        ignores: t.FrozenSet[str] = frozenset(),
    ) -> None:
        if search_scopes is None:
            search_scopes = sys.path
        self.top_name_2_path = self._index_top_names(
            search_scopes, search_paths
        )
        
        self.known_stdlib_module_names = frozenset((
            # ref: https://github.com/mgedmin/findimports/blob/master
            #   /findimports.py
            # taken from python 3.12
            '__future__',
            '_abc', '_aix_support', '_ast', '_asyncio',
            '_bisect', '_blake2', '_bootsubprocess', '_bz2',
            '_codecs', '_codecs_cn', '_codecs_hk', '_codecs_iso2022',
            '_codecs_jp', '_codecs_kr', '_codecs_tw', '_collections',
            '_collections_abc', '_compat_pickle', '_compression',
            '_contextvars', '_crypt', '_csv', '_ctypes', '_curses',
            '_curses_panel',
            '_datetime', '_dbm', '_decimal',
            '_elementtree',
            '_frozen_importlib', '_frozen_importlib_external', '_functools',
            '_gdbm',
            '_hashlib', '_heapq',
            '_imp', '_io',
            '_json',
            '_locale', '_lsprof', '_lzma',
            '_markupbase', '_md5', '_msi', '_multibytecodec',
            '_multiprocessing',
            '_opcode', '_operator', '_osx_support', '_overlapped',
            '_pickle', '_posixshmem', '_posixsubprocess', '_py_abc',
            '_pydecimal', '_pyio',
            '_queue',
            '_random',
            '_sha1', '_sha256', '_sha3', '_sha512', '_signal', '_sitebuiltins',
            '_socket', '_sqlite3', '_sre', '_ssl', '_stat', '_statistics',
            '_string', '_strptime', '_struct', '_symtable',
            '_thread', '_threading_local', '_tkinter', '_tracemalloc',
            '_uuid',
            '_warnings', '_weakref', '_weakrefset', '_winapi',
            '_zoneinfo',
            'abc', 'aifc', 'antigravity', 'argparse', 'array', 'ast',
            'asynchat', 'asyncio', 'asyncore', 'atexit', 'audioop',
            'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins', 'bz2',
            'cProfile', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd',
            'code', 'codecs', 'codeop', 'collections', 'colorsys', 'compileall',
            'concurrent', 'configparser', 'contextlib', 'contextvars', 'copy',
            'copyreg', 'crypt', 'csv', 'ctypes', 'curses',
            'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib', 'dis',
            'distutils', 'doctest',
            'email', 'encodings', 'ensurepip', 'enum', 'errno',
            'faulthandler', 'fcntl', 'filecmp', 'fileinput', 'fnmatch',
            'fractions', 'ftplib', 'functools',
            'gc', 'genericpath', 'getopt', 'getpass', 'gettext', 'glob',
            'graphlib', 'grp', 'gzip',
            'hashlib', 'heapq', 'hmac', 'html', 'http',
            'idlelib', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect', 'io',
            'ipaddress', 'itertools',
            'json',
            'keyword',
            'lib2to3', 'linecache', 'locale', 'logging', 'lzma',
            'mailbox', 'mailcap', 'marshal', 'math', 'mimetypes', 'mmap',
            'modulefinder', 'msilib', 'msvcrt', 'multiprocessing',
            'netrc', 'nis', 'nntplib', 'nt', 'ntpath', 'nturl2path', 'numbers',
            'opcode', 'operator', 'optparse', 'os', 'ossaudiodev',
            'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil',
            'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint',
            'profile', 'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc',
            'pydoc_data', 'pyexpat',
            'queue', 'quopri',
            'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter',
            'runpy', 'sched',
            'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil',
            'signal', 'site', 'smtpd', 'smtplib', 'sndhdr', 'socket',
            'socketserver', 'spwd', 'sqlite3', 'sre_compile', 'sre_constants',
            'sre_parse', 'ssl', 'stat', 'statistics', 'string', 'stringprep',
            'struct', 'subprocess', 'sunau', 'symtable', 'sys', 'sysconfig',
            'syslog',
            'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios',
            'textwrap', 'this', 'threading', 'time', 'timeit', 'tkinter',
            'token', 'tokenize', 'tomllib', 'trace', 'traceback', 'tracemalloc',
            'tty', 'turtle', 'turtledemo', 'types', 'typing',
            'unicodedata', 'unittest', 'urllib', 'uu', 'uuid',
            'venv',
            'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound',
            'wsgiref',
            'xdrlib', 'xml', 'xmlrpc',
            'zipapp', 'zipfile', 'zipimport', 'zlib',
        ))
        self.ignores = ignores
        
        self.module_name_2_file = {}
        for name in self.known_stdlib_module_names:
            self.module_name_2_file[name] = '<stdlib>'
        for name, (path, isdir) in self.top_name_2_path.items():
            if not isdir:
                self.module_name_2_file[name] = path
        # print(self.module_name_2_file, ':vl')
        # print(self.module_name_2_file['lk_utils'], ':v')
        # if input('continue: ') == 'x':
        #     sys.exit()
    
    def _index_top_names(
        self,
        search_scopes: t.Iterable[str],
        search_paths: t.Iterable[str] = (),
    ) -> t.Dict[str, t.Tuple[str, bool]]:
        # {str top_name: (path, is_dir), ...}
        top_name_2_path = {}
        for root in map(fs.abspath, search_scopes):
            for d in fs.find_dirs(root):
                # print(d.name, ':v')
                if '.' not in d.name and d.name != '__pycache__':
                    # if fs.exists(x := '{}/__init__.py'.format(d.path)):
                    #     top_name_2_path[d.name] = (x, False)
                    # else:
                    #     top_name_2_path[d.name] = (d.path, True)
                    # assert fs.exists(x := '{}/__init__.py'.format(d.path)), d.path
                    # top_name_2_path[d.name] = (x, False)
                    top_name_2_path[d.name] = (d.path, True)
            for f in fs.find_files(root):
                if '.' not in f.stem:
                    top_name_2_path[f.stem] = (f.path, False)
        for p in map(fs.abspath, search_paths):
            top_name_2_path[fs.basename(p, suffix=False)] = (p, fs.isdir(p))
        return top_name_2_path
    
    def is_stdlib_module(self, module_name: T.ModuleName) -> bool:
        if '.' in module_name:
            return module_name.split('.', 1)[0] in \
                self.known_stdlib_module_names
        return module_name in self.known_stdlib_module_names
    
    def find_module_path(self, module: T.ModuleInfo) -> T.Path:
        if module.id in self.module_name_2_file:
            return self.module_name_2_file[module.id]
        if module.name in self.module_name_2_file:
            # a.
            # return self.module_name_2_file[module.name]
            # b.
            # out = self.module_name_2_file[module.name]
            # self.module_name_2_file[module.id] = out
            # return out
            # c.
            out = self.module_name_2_file[module.name]
            if not out.endswith('/__init__.py'):
                self.module_name_2_file[module.id] = out
                return out
        
        if module.top in self.known_stdlib_module_names:
            self.module_name_2_file[module.id] = '<stdlib>'
            return '<stdlib>'
        if module.name in self.ignores or module.id in self.ignores:
            self.module_name_2_file[module.id] = '<ignored>'
            return '<ignored>'
        
        def determine_path() -> T.Path:
            if module.base_dir:
                base_dir = module.base_dir
                module_path = '{}/{}'.format(
                    base_dir, module.relname.replace('.', '/')
                ).rstrip('/')
            else:
                try:
                    x = self.top_name_2_path[module.top]
                except KeyError:
                    raise ModuleNotFound(module)
                # assert x[1], (module, x[0])
                if x[1]:
                    base_dir = x[0]
                    module_path = '{}/{}'.format(
                        base_dir,
                        module.name
                        .replace(module.top, '', 1)
                        .lstrip('.')
                        .replace('.', '/')
                    ).rstrip('/')
                else:
                    # e.g.
                    #   module = ModuleInfo(
                    #       name='typing_extensions',
                    #       end='Literal',
                    #       level=0,
                    #       base_dir=None,
                    #   )
                    #   x = ('<site_packages>/typing_extensions.py', False)
                    # return x[0]
                    raise Exception('impossible case', module, x)
            if fs.isdir(module_path):
                if module.end in ('', '*'):
                    assert fs.exists(x := '{}/__init__.py'.format(module_path))
                    self.module_name_2_file[module.id] = x
                    self.module_name_2_file[module.name] = x
                    return x
                else:
                    # if fs.exists(x := '{}/__init__.py'.format(module_path)):
                    #     if module.end:
                    #         if re.match(r'__[a-zA-Z0-9]+__', module.end):
                    #             # e.g. '__file__', '__path__', '__spec__', ...
                    #             return x
                    #         tree = ast.parse(fs.load(x), x)
                    #         for node in ast.walk(tree):
                    #             if isinstance(node, (ast.Import, ast.ImportFrom)):
                    #                 for alias in node.names:
                    #                     if (
                    #                         alias.name == module.end or
                    #                         alias.asname == module.end
                    #                     ):
                    #                         return x
                    #     else:
                    #         return x
                    for f in fs.find_files(
                        module_path, ('.py', '.pyc', '.pyd')
                    ):
                        if f.stem == module.end:
                            self.module_name_2_file[module.id] = f.path
                            return f.path
                    for d in fs.find_dirs(module_path):
                        if d.name == module.end:
                            if fs.exists(x := '{}/__init__.py'.format(d.path)):
                                self.module_name_2_file[module.id] = x
                                return x
                            else:
                                raise PathNotFound(module)
                    if fs.exists(x := '{}/__init__.py'.format(module_path)):
                        self.module_name_2_file[module.id] = x
                        self.module_name_2_file[module.name] = x
                        return x
                raise ModuleNotFound(module)
            else:
                parent_dir, parent_name = module_path.rsplit('/', 1)
                # print(':vl', parent_dir, fs.find_file_names(parent_dir))
                for f in fs.find_files(parent_dir, ('.py', '.pyc', '.pyd')):
                    if f.stem == parent_name:
                        self.module_name_2_file[module.name] = f.path
                        self.module_name_2_file[module.id] = f.path
                        return f.path
                else:
                    raise PathNotFound(module)
        
        assert (out := determine_path())
        # self.module_name_2_file[module.id] = out
        return out


class ModuleNotFound(Exception):
    """
    module not found.
    possible reasons:
        - it is an optional dependency that not installed in venv or
            site-packages.
        - it is a function/class/variable/builtin name not a module name in
            source.
    """
    pass


class PathNotFound(Exception):
    pass
