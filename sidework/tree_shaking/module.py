import ast
import sys
import typing as t

from lk_utils import fs


class T:
    ModuleName = str
    Path = str  # normalized absolute path


class ModuleInspector:
    
    def __init__(
        self,
        search_scopes: t.Iterable[str] = None,
        search_paths: t.Iterable[str] = (),
    ) -> None:
        if search_scopes is None:
            search_scopes = sys.path
        self.top_name_2_path = self._index_top_names(
            search_scopes, search_paths
        )
        
        self.known_stdlib_module_names = frozenset((
            # taken from Python 3.10
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
            'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty',
            'turtle', 'turtledemo', 'types', 'typing',
            'unicodedata', 'unittest', 'urllib', 'uu', 'uuid',
            'venv',
            'warnings', 'wave', 'weakref', 'webbrowser', 'winreg', 'winsound',
            'wsgiref',
            'xdrlib', 'xml', 'xmlrpc',
            'zipapp', 'zipfile', 'zipimport',
        ))
        
        self.module_name_2_path = {}
        for name in self.known_stdlib_module_names:
            self.module_name_2_path[name] = '<stdlib>'
        for name, (path, isdir) in self.top_name_2_path.items():
            if not isdir:
                self.module_name_2_path[name] = path
        # print(self.module_name_2_path['lk_utils'], ':v')
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
                if '.' not in d.name and d.name != '__pycache__':
                    if fs.exists(x := '{}/__init__.py'.format(d.path)):
                        top_name_2_path[d.name] = (x, False)
                    else:
                        top_name_2_path[d.name] = (d.path, True)
                    # assert fs.exists(x := '{}/__init__.py'.format(d.path)), d.path
                    # top_name_2_path[d.name] = (x, False)
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
    
    def get_module_path(
        self, module_name: T.ModuleName, base: T.Path = None
    ) -> T.Path:
        if module_name in self.module_name_2_path:
            return self.module_name_2_path[module_name]
        
        print(module_name, ':p')
        match module_name.count('.'):
            case 0:
                top = parent = name = module_name
            case 1:
                top, name = module_name.split('.', 1)
                parent = top
            case _:
                top = module_name.split('.', 1)[0]
                parent, name = module_name.rsplit('.', 1)
        # assert top in self.module_name_2_path, (
        #     'unindexed module', module_name, base
        # )
        
        if top in self.known_stdlib_module_names:
            self.module_name_2_path[module_name] = '<stdlib>'
            return '<stdlib>'
        
        def determine_path() -> T.Path:
            try:
                top_path = base if base else self.top_name_2_path[top][0]
            except KeyError:
                raise PathNotFound(module_name, top)
            parent_path = '{}/{}'.format(top_path, parent.replace('.', '/'))
            # if parent_path.endswith('/api'):  # TEST
            #     print(
            #         ':vl',
            #         fs.isdir(parent_path),
            #         fs.exists('{}/__init__.py'.format(parent_path))
            #     )
            if fs.isdir(parent_path):
                if fs.exists(x := '{}/__init__.py'.format(parent_path)):
                    if parent == name:
                        return x
                    tree = ast.parse(fs.load(x), x)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.Import, ast.ImportFrom)):
                            for alias in node.names:
                                if (
                                    alias.name == name or
                                    alias.asname == name
                                ):
                                    return x
                for f in fs.find_files(parent_path, ('.py', '.pyc', '.pyd')):
                    if f.stem == name:
                        return f.path
                for d in fs.find_dirs(parent_path):
                    if d.name == name:
                        if fs.exists(x := '{}/__init__.py'.format(d.path)):
                            return x
                        else:
                            raise PathNotFound(module_name, parent_path, name)
            else:
                parent_dir, parent_name = parent_path.rsplit('/', 1)
                # print(':vl', parent_dir, fs.find_file_names(parent_dir))
                for f in fs.find_files(parent_dir, ('.py', '.pyc', '.pyd')):
                    if f.stem == parent_name:
                        return f.path
                else:
                    raise PathNotFound(
                        module_name, parent_dir, parent_name, name
                    )
        
        assert (out := determine_path())
        self.module_name_2_path[module_name] = out
        return out


class PathNotFound(Exception):
    pass
