import os
import re
import sys
import typing as t
from collections import defaultdict

from lk_utils import fs
from lk_utils import loads
from lk_utils import run_cmd_args
from lk_utils.read_and_write import ropen

from ... import normalization as norm
from ...utils import verspec

_poetry = (sys.executable, '-m', 'poetry')


# noinspection PyTypedDict
class T:
    ExactVersion = str
    PackageId = str  # str['{name}-{version}']
    PackageName = str
    PathName = str  # union[dir_name, file_name, bin_name]  # DELETE
    Path = str  # an absolute path
    
    PackageInfo0 = t.TypedDict(
        'PackageInfo0',
        {
            'package_id': PackageId,
            'version': ExactVersion,
            'url': str,
            'paths': t.Iterable[PathName],
            'dependencies': t.List[PackageName],
        },
    )
    PackageInfo1 = t.TypedDict(
        'PackageInfo1',
        {
            'package_name': PackageName,
            'version': ExactVersion,
            'url': str,
            'paths': t.Iterable[PathName],
            'dependencies': t.List[PackageId],
        },
    )
    
    Packages0 = t.Dict[PackageName, PackageInfo0]
    Packages1 = t.Dict[PackageName, PackageInfo1]  # TODO: not used


def get_venv_root(working_root: str) -> str:  # DELETE: internal use only
    print(working_root, ':pv')
    return fs.abspath(
        run_cmd_args(
            _poetry, 'env', 'info', '--path', '-C', working_root
        ).strip()
    )


def get_venv_packages_root(working_root: str) -> str:
    venv_root = get_venv_root(working_root)
    if os.name == 'nt':
        return f'{venv_root}/Lib/site-packages'
    else:
        return '{}/lib/python{}.{}/site-packages'.format(
            venv_root, sys.version_info.major, sys.version_info.minor
        )


class PackagesIndex:
    packages: T.Packages0
    packages_root: str
    working_root: str
    
    def __init__(self, working_root: T.Path):
        """
        venv_root: this can be got by `get_target_venv_packages_dir()`. see \
            usage at `depsland/manifest/manifest.py:Manifest \
            ._update_dependencies()`.
        """
        self.working_root = working_root
        self.packages_root = get_venv_packages_root(working_root)
        print(self.packages_root, ':lv')
        
        # self.packages = self.index_packages()
        self.packages = self.index_packages_2()
        # print(self.packages_root, self.packages, ':lv')
    
    # -------------------------------------------------------------------------
    
    def index_packages(self) -> T.Packages0:  # DELETE
        all_pkgs = self._get_all_packages()
        top_pkgs = self._get_top_packages(all_pkgs)
        self._fill_dependencies(top_pkgs)
        return top_pkgs
    
    def _get_all_packages(self) -> T.Packages0:
        def find_dist_info_dirs() -> t.Iterator[t.Tuple[str, str]]:
            for d in fs.find_dirs(self.packages_root):
                if d.name.endswith('.dist-info'):
                    yield d.name, d.path
        
        def get_custom_url(pkg_dir: str) -> t.Optional[str]:
            if fs.exists(f := f'{pkg_dir}/direct_url.json'):
                data = loads(f)
                return data['url']
            return None
        
        out: T.Packages0 = {}  # noqa
        
        for dname, dpath in find_dist_info_dirs():
            name, ver = norm.split_dirname_of_dist_info(dname)
            pkg_id = f'{name}-{ver}'
            url = get_custom_url(dpath)
            
            record_file = f'{dpath}/RECORD'
            assert fs.exists(record_file)
            
            path_names = set(self._analyze_records(record_file))

            print(name, ':i2')
            assert name not in out, (
                (
                    'currently we do not support one package with multiple '
                    'versions installed in same environment'
                ),
                (name, out[name]['version'], ver),
            )
            # noinspection PyTypeChecker
            out[name] = {
                'package_id': pkg_id,
                'version': ver,
                'url': url or '',
                'paths': sorted(path_names),
                'dependencies': [],
            }
            
        return out
    
    def _get_top_packages(self, all_packages: T.Packages0) -> T.Packages0:
        return {
            k: all_packages[k]
            for k in get_top_level_package_names(self.working_root)
        }
    
    def _fill_dependencies(self, top_packages: T.Packages0) -> T.Packages0:
        
        def get_sub_packages() -> t.Iterator[t.Tuple[T.PackageName, T.PackageName]]:
            content = run_cmd_args(
                _poetry,
                ('show', '-t', '--no-dev'),
                ('--directory', self.working_root),
            )
            
            re_lv0 = re.compile(r'^\w+')
            re_lv1 = re.compile(r'^├── ([-\w]+)')
            
            parent_name = ''
            for line in content.splitlines():
                if m := re_lv0.match(line):
                    parent_name = m.group()
                elif m := re_lv1.match(line):
                    assert parent_name
                    yield parent_name, m.group(1)
        
        for parent_name, sub_name in get_sub_packages():
            # assert parent_name in top_packages
            top_packages[parent_name]['dependencies'].append(sub_name)
        return top_packages
    
    # -------------------------------------------------------------------------
    
    def index_packages_2(self) -> T.Packages0:
        all_pkgs = self._get_all_packages()
        relations = self._analyze_deps_relations(all_pkgs)
        for name, deps in relations.items():
            all_pkgs[name]['dependencies'].extend(sorted(deps))
        return all_pkgs
    
    def _analyze_deps_relations(
        self, packages: T.Packages0
    ) -> t.Dict[T.PackageName, t.Set[T.PackageName]]:
        out = defaultdict(set)
        
        for dname, dpath in self._find_dist_info_dirs(self.working_root):
            parent_name, _ = norm.split_dirname_of_dist_info(dname)
            assert parent_name in packages
            
            metadata_file = f'{dpath}/METADATA'
            if fs.exists(metadata_file):
                for sub_name, verspecs in self._analyze_metadata(metadata_file):
                    if sub_name in packages:
                        exact_version = packages[sub_name]['version']
                        assert (
                            verspec.find_proper_version(
                                *verspecs, candidates=(exact_version,)
                            )
                            == exact_version
                        )
                        out[parent_name].add(sub_name)
                    else:
                        print(':lv4', sorted(packages.keys()), sub_name)
                        raise Exception(sub_name)
        return out
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _find_dist_info_dirs(root: str) -> t.Iterator[t.Tuple[str, str]]:
        for d in fs.find_dirs(root):
            if d.name.endswith('.dist-info'):
                yield d.name, d.path
    
    @staticmethod
    def _get_custom_url(pkg_dir: str) -> t.Optional[str]:
        if fs.exists(f := f'{pkg_dir}/direct_url.json'):
            data = loads(f)
            return data['url']
        return None
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _analyze_metadata(
        file: str,
    ) -> t.Iterator[t.Tuple[T.PackageName, t.Iterator[verspec.VersionSpec]]]:
        pattern = re.compile(r'([-\w]+)(?: \(([^)]+)\))?')  # fmt:skip
        #                      ^~~~~~~1      ^~~~~~2        # fmt:skip
        #   e.g. 'argsense (>=0.4.2,<0.5.0)' -> ('argsense', '>=0.4.2,<0.5.0')
        
        def walk() -> t.Iterator[str]:
            with ropen(file) as f:
                flag = 0
                head = 'Requires-Dist: '
                for line in f:
                    if not line:
                        break
                    if flag == 0:
                        if line.startswith(head):
                            flag = 1
                        else:
                            continue
                    else:
                        if not line.startswith(head):
                            break
                    # assert flag == 1
                    yield norm.normalize_name(line[len(head):])
        
        for line in walk():
            if ';' in line:
                # e.g. 'Requires-Dist: toml; extra == "ext"'
                continue
            try:
                raw_name, raw_verspec = pattern.match(line).groups()
            except AttributeError as e:
                print(':lv4', file, line, e)
                raise e
            name = norm.normalize_name(raw_name)
            verspecs = norm.normalize_version_spec(name, raw_verspec or '')
            yield name, verspecs
    
    @staticmethod
    def _analyze_records(file: str) -> t.Iterator[T.PathName]:
        records = loads(file, 'plain').splitlines()
        for line in records:
            path = fs.normpath(line.rsplit(',', 2)[0])
            if path.startswith('../'):
                # e.g. '../../../bin/dulwich'
                # TODO: currently we don't take account of this case.
                print(':vs', 'discard external binary', path)
                continue
                # assert path.lstrip('./').startswith('bin/')
                # raise Exception(path)
            elif path.startswith('bin/'):
                name = 'bin/{}'.format(path[4:].split('/', 1)[0])
            else:
                name = path.split('/', 1)[0]
            yield name


def get_top_level_package_names(working_root: str) -> t.Iterator[T.PackageName]:
    # note: there is a bug in `poetry show -T` so we don't use it.
    #   instead we use `poetry show -t` and manually parse the output.
    content = run_cmd_args(
        _poetry,
        ('show', '-t', '--no-dev'),
        ('--directory', working_root),
    )
    re_pkg_name = re.compile(r'^[-\w]+')
    for line in content.splitlines():
        if m := re_pkg_name.match(line):
            yield norm.normalize_name(m.group())
