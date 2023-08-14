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


def get_target_venv_root(target_working_dir: str) -> str:
    print(target_working_dir, ':pv')
    poetry_cli = (sys.executable, '-m', 'poetry')
    return fs.abspath(
        run_cmd_args(
            poetry_cli, 'env', 'info', '--path', '-C', target_working_dir
        )
    )


class PackagesIndex:
    packages: T.Packages0
    root: str
    
    def __init__(self, venv_root: str):
        self.root = venv_root
        self.packages = self.index_packages(self.root)
    
    # -------------------------------------------------------------------------
    
    def index_packages(self, root: str) -> T.Packages0:
        out: T.Packages0 = {}  # noqa
        
        for dname, dpath in self._find_dist_info_dirs(root):
            name, ver = norm.split_dirname_of_dist_info(dname)
            parent_name = f'{name}-{ver}'
            url = self._get_custom_url(dpath)
            
            record_file = f'{dpath}/RECORD'
            assert fs.exists(record_file)
            
            path_names = set(self._analyze_records(record_file))
            
            assert name not in out, (
                (
                    'currently we do not support one package with multiple '
                    'versions installed in same environment'
                ),
                (name, out[name]['version'], ver),
            )
            # noinspection PyTypeChecker
            out[name] = {
                'package_id': parent_name,
                'version': ver,
                'url': url or '',
                'paths': sorted(path_names),
                'dependencies': [],
            }
        
        relations = self.analyze_deps_relations(root, out)
        for parent_name, children_names in relations.items():
            out[parent_name]['dependencies'].extend(sorted(children_names))
        
        return out
    
    def analyze_deps_relations(
        self, root: str, packages: T.Packages0
    ) -> t.Dict[T.PackageName, t.Set[T.PackageName]]:
        out = defaultdict(set)
        
        for dname, dpath in self._find_dist_info_dirs(root):
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
                        print(':lv4', packages, sub_name)
                        raise Exception(sub_name)
        return out
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _find_dist_info_dirs(root: str) -> t.Iterator[t.Tuple[str, str]]:
        for d in fs.find_dirs(root):
            if d.name.endswith('.dist-info'):
                yield d
    
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
                    yield line[len(head):]
        
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
                raise Exception(path)
            elif path.startswith('bin/'):
                name = 'bin/{}'.format(path[4:].split('/', 1)[0])
            else:
                name = path.split('/', 1)[0]
            yield name


def get_top_level_package_names(root: str) -> t.Iterator[T.PackageName]:
    # note: there is a bug in `poetry show -T` so we don't use it.
    #   instead we use `poetry show -t` and manually parse the output.
    content = run_cmd_args(
        (sys.executable, '-m', 'poetry'),
        ('show', '-t', '--no-dev'),
        ('--directory', root),
    )
    re_pkg_name = re.compile(r'^[-\w]+')
    for line in content.splitlines():
        if m := re_pkg_name.match(line):
            yield m.group()
