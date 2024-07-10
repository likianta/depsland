import typing as t
from dataclasses import dataclass
from functools import cached_property

from lk_utils import fs
from .path_scope import path_scope


@dataclass
class ModuleInfo:
    name0: str  # e.g. 'a.b.c'
    name1: str  # e.g. 'b.c'
    name2: str  # e.g. 'd'
    level: int  # e.g. 1
    base_dir: t.Optional[str]  # e.g. '<path/to/a>'
    full_name: str = None  # e.g. 'a.b.c.d'
    
    # def __str__(self) -> str:
    #     return self.id
    
    @cached_property
    def relname(self) -> str:
        if self.level:
            return '.'.join(self.name0.split('.')[self.level:])
        return self.name0
    
    @cached_property
    def id(self) -> str:
        return '{}.{}'.format(self.name0, self.name2).rstrip('.')
    
    @cached_property
    def top(self) -> str:
        return self.name0.split('.', 1)[0]


class T:
    ModuleId = str
    ModuleInfo = ModuleInfo
    ModuleName = str
    Path = str  # normalized absolute path


# noinspection PyMethodMayBeStatic
class ModuleInspector:
    known_stdlib_module_names: t.FrozenSet[str]
    module_name_2_file: t.Dict[T.ModuleId, T.Path]
    
    def __init__(self, ignores: t.Iterable[str] = ()) -> None:
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
        
        self.module_name_2_file = {}
        for name in self.known_stdlib_module_names:
            self.module_name_2_file[name] = '<stdlib>'
        for name in ignores:
            self.module_name_2_file[name] = '<ignored>'
        for name, (path, isdir) in path_scope.module_2_path.items():
            if not isdir:
                self.module_name_2_file[name] = path
        # print(self.module_name_2_file['typing_extensions'], ':v')
        # print(self.module_name_2_file, ':vl')
        # print(self.module_name_2_file['lk_utils'], ':v')
        # if input('continue: ') == 'x':
        #     import sys
        #     sys.exit()
    
    def find_module_path(self, module: T.ModuleInfo) -> T.Path:
        if module.id in self.module_name_2_file:
            module.full_name = module.id.removesuffix('.*')
            return self.module_name_2_file[module.id]
        if module.name0 in self.module_name_2_file:
            out = self.module_name_2_file[module.name0]
            if out in ('<stdlib>', '<ignored>'):
                if module.name2:
                    self.module_name_2_file[module.id] = out
                return out
            if module.name2 in ('', '*'):
                module.full_name = module.name0
                self.module_name_2_file[module.id] = out
                return out
            else:
                if out.endswith('/__init__.py'):
                    pass
                else:
                    module.full_name = module.name0
                    self.module_name_2_file[module.id] = out
                    return out
        
        if module.top in self.known_stdlib_module_names:
            self.module_name_2_file[module.id] = '<stdlib>'
            return '<stdlib>'
        
        def determine_path() -> T.Path:
            if module.base_dir:
                if module.name1:
                    if module.name2 not in ('', '*'):
                        if x := self._quick_check_path(
                            '{}/{}/{}'.format(
                                module.base_dir,
                                module.name1.replace('.', '/'),
                                module.name2
                            ),
                            case_sensitive=True
                        ):
                            module.full_name = module.id
                            self.module_name_2_file[module.id] = x
                            return x
                    if x := self._quick_check_path('{}/{}'.format(
                        module.base_dir, module.name1.replace('.', '/')
                    )):
                        module.full_name = module.name0
                        self.module_name_2_file[module.name0] = x
                        self.module_name_2_file[module.id] = x
                        return x
                else:
                    if module.name2 in ('', '*'):
                        raise Exception('unreachable case')
                    else:
                        if x := self._quick_check_path(
                            '{}/{}'.format(module.base_dir, module.name2),
                            case_sensitive=True
                        ):
                            module.full_name = module.id
                            self.module_name_2_file[module.id] = x
                            return x
            else:
                try:
                    top_path, isdir = path_scope.module_2_path[module.top]
                except KeyError:
                    raise ModuleNotFound(module)
                # assert x[1], (module, x[0])
                if isdir:
                    if module.name2 not in ('', '*'):
                        if x := self._quick_check_path(
                            '{}/{}/{}'.format(
                                top_path,
                                module.name0
                                    .replace(module.top, '', 1)
                                    .lstrip('.')
                                    .replace('.', '/'),
                                module.name2
                            ).replace('//', '/'),
                            case_sensitive=True
                        ):
                            module.full_name = module.id
                            self.module_name_2_file[module.id] = x
                            return x
                    if x := self._quick_check_path(
                        '{}/{}'.format(
                            top_path,
                            '' if module.name0 == module.top else
                            module.name0
                                .replace(module.top, '', 1)
                                .lstrip('.')
                                .replace('.', '/'),
                        ).rstrip('/')
                    ):
                        # if module.name0 == 'lk_utils':
                        #     print(':v', module, x)
                        #     _debug_interrupt()
                        module.full_name = module.name0
                        self.module_name_2_file[module.name0] = x
                        self.module_name_2_file[module.id] = x
                        return x
                else:
                    module.full_name = module.top
                    self.module_name_2_file[module.name0] = top_path
                    self.module_name_2_file[module.id] = top_path
                    return top_path
            raise ModuleNotFound(module)
        
        assert (out := determine_path())
        return out
    
    def _quick_check_path(
        self, possible_path: str, case_sensitive: bool = False
    ) -> t.Optional[T.Path]:
        if fs.isdir(possible_path):
            if fs.exists(x := f'{possible_path}/__init__.py'):
                return x
        if case_sensitive:
            a, b = possible_path.rsplit('/', 1)
            for f in fs.find_files(a, ('.py', '.pyc', '.pyd')):
                if f.stem == b:
                    return f.path
        else:
            for ext in ('.py', '.pyc', '.pyd'):
                if fs.exists(x := possible_path + ext):
                    return x


def _debug_interrupt() -> None:
    if input('continue: ') == 'x':
        import sys
        sys.exit()


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
