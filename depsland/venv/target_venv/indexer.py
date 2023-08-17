"""
the concept of terms:
    library
        package 0
        package 1
        package 2
        ...
"""
import re
import sys
import typing as t

from lk_utils import fs
from lk_utils import loads
from lk_utils import run_cmd_args
from lk_utils.read_and_write import ropen

from . import finder
from ... import normalization as norm
from ...utils import verspec


# noinspection PyTypedDict
class T:
    ExactVersion = str
    PackageId = str  # str['{name}-{version}']
    PackageName = str
    PathName = str  # union[dir_name, file_name, bin_name]  # DELETE
    Path = str  # an absolute path
    
    PackageInfo = t.TypedDict(
        'PackageInfo',
        {
            'package_id': PackageId,
            'version': ExactVersion,
            'url': str,
            'paths': t.Iterable[PathName],
            'dependencies': t.List[PackageName],
        },
    )
    PackageReferences = t.Dict[PackageName, t.Tuple[str, Path]]
    Packages = t.Dict[PackageName, PackageInfo]


# -----------------------------------------------------------------------------


def index_all_package_references(
    library_root: T.Path,
) -> t.Iterator[t.Tuple[T.PackageName, t.Tuple[str, T.Path]]]:
    """this is for quick indexing that is faster than `index_packages`"""
    for dname, dpath in _find_dist_info_dirs(library_root):
        pkg_name, _ = norm.split_dirname_of_dist_info(dname)
        yield pkg_name, (dname, dpath)


def _find_dist_info_dirs(library_root: T.Path) -> t.Iterator[t.Tuple[str, str]]:
    for d in fs.find_dirs(library_root):
        if d.name.endswith('.dist-info'):
            yield d.name, d.path


def _get_custom_url(pkg_dir: str) -> t.Optional[str]:
    if fs.exists(f := f'{pkg_dir}/direct_url.json'):
        data = loads(f)
        return data['url']
    return None


# -----------------------------------------------------------------------------


class LibraryIndexer:
    library_root: T.Path
    packages: T.Packages
    working_root: T.Path
    
    def __init__(self, working_root: T.Path):
        """
        venv_root: this can be got by `get_target_venv_packages_dir()`. see \
            usage at `depsland/manifest/manifest.py:Manifest \
            ._update_dependencies()`.
        """
        print(':t2s')
        
        self.working_root = working_root
        self.library_root = finder.get_library_root(working_root)
        print(self.library_root)
        
        # self._all_pgk_refs = dict(quick_index_packages(self.library_root))
        self.packages = self.index_packages()
        # print(self.library_root, self.packages, ':lv')
        # print(
        #     {
        #         (i, k): len(v['dependencies'])
        #         for i, (k, v) in enumerate(sorted(self.packages.items()), 1)
        #     },
        #     ':lv',
        # )
        print(':t2', 'indexing packages done', len(self.packages))
    
    # -------------------------------------------------------------------------
    
    def index_packages(self) -> T.Packages:
        all_pgk_refs: T.PackageReferences = dict(
            index_all_package_references(self.library_root)
        )
        top_pkg_names = finder.get_top_package_names_by_poetry(
            self.working_root
        )
        print(len(all_pgk_refs))
        
        top_pkgs: T.Packages = {}
        for top_name in top_pkg_names:
            print(':i2', top_name)
            # assert top_name in all_pgk_refs
            # assert top_name not in top_pkgs, (
            #     (
            #         'currently we do not support one package with multiple '
            #         'versions installed in same environment'
            #     ),
            #     (top_name, top_pkgs[top_name]['version']),
            # )
            dname, dpath = all_pgk_refs[top_name]  # dist-info dir
            top_pkgs[top_name] = self._create_package_info(dname, dpath)
        self._fill_dependencies(top_pkgs)
        # print(top_pkgs, ':lv')
        
        before = len(top_pkgs)
        out = self._flatten_packages(top_pkgs, all_pgk_refs)
        # print(out, ':lv')
        after = len(out)
        print('flatten packages done', f'count: {before} -> {after}', ':v2')
        return out
    
    @staticmethod
    def _create_package_info(dname: str, dpath: T.Path) -> T.PackageInfo:
        name, ver = norm.split_dirname_of_dist_info(dname)
        pkg_id = f'{name}-{ver}'
        url = _get_custom_url(dpath)
        
        record_file = f'{dpath}/RECORD'
        assert fs.exists(record_file)
        path_names = set(analyze_records(record_file))
        
        return {
            'package_id': pkg_id,
            'version': ver,
            'url': url or '',  # noqa
            'paths': tuple(sorted(path_names)),
            'dependencies': [],
        }
    
    def _fill_dependencies(self, packages: T.Packages) -> None:
        """
        notice: this method only works for top-level packages. i.e. it is not \
        available for `self._flatten_packages`.
        """
        
        def get_secondary_packages() -> (
            t.Iterator[t.Tuple[T.PackageName, T.PackageName]]
        ):
            _poetry = (sys.executable, '-m', 'poetry')
            content = run_cmd_args(
                _poetry,
                ('show', '-t', '--no-dev', '--no-ansi'),
                ('--directory', self.working_root),
            )
            
            re_lv0 = re.compile(r'^[-\w]+')
            re_lv1 = re.compile(r'^\W\W\W ([-\w]+)')
            
            name0 = ''
            for line in content.splitlines():
                if m := re_lv0.match(line):
                    name0 = norm.normalize_name(m.group())
                elif m := re_lv1.match(line):
                    assert name0
                    name1 = norm.normalize_name(m.group(1))
                    yield name0, name1
        
        for pkg_name, dep_name in get_secondary_packages():
            # assert parent_name in top_packages
            packages[pkg_name]['dependencies'].append(dep_name)
    
    @staticmethod
    def _fill_dependencies_2(  # not used.
        packages: T.Packages,
        # base_packages: T.Packages,
        all_package_references: T.PackageReferences,
    ) -> None:
        """another implementation, based on metadata."""
        for name, v in packages.items():
            # print(':i2', 'filling an indirect package', name)
            _, dpath = all_package_references[name]
            metadata_file = f'{dpath}/METADATA'
            if fs.exists(metadata_file):
                for dep_name, verspecs in analyze_metadata(metadata_file):
                    v['dependencies'].append(dep_name)
                    # TODO: check the `verspecs` match existed info in \
                    #   `packages` or info in `all_package_references`.
                    # if dep_name in packages:
                    #     exact_version = packages[dep_name]['version']
                    #     assert (
                    #         verspec.find_proper_version(
                    #             *verspecs, candidates=(exact_version,)
                    #         )
                    #         == exact_version
                    #     )
                    # else:
                    #     ...
    
    def _flatten_packages(
        self, packages: T.Packages, all_package_references: T.PackageReferences
    ) -> T.Packages:
        nested: T.Packages = packages
        flatten: T.Packages = packages.copy()
        
        def recurse(unindexed_names: t.Sequence[T.PackageName]) -> None:
            """
            result: the nonlocal `flatten` gets updated.
            """
            temp: T.Packages = {}
            for name in unindexed_names:
                dname, dpath = all_package_references[name]
                info = self._create_package_info(dname, dpath)
                temp[name] = info
            self._fill_dependencies_2(temp, all_package_references)
            flatten.update(temp)
            if x := tuple(collect_unindexed_names(temp, flatten)):
                recurse(x)
        
        def collect_unindexed_names(
            nested: T.Packages, flatten: T.Packages
        ) -> t.Iterator[T.PackageName]:
            for v in nested.values():
                for name in v['dependencies']:
                    if name not in flatten:
                        yield name
        
        if x := tuple(collect_unindexed_names(nested, flatten)):
            recurse(x)
        return flatten


# -----------------------------------------------------------------------------


def analyze_metadata(
    metadata_file: str,
) -> t.Iterator[t.Tuple[T.PackageName, t.Iterator[verspec.VersionSpec]]]:
    """
    all possibile line cases:
        Requires-Dist: colorama; os_name == "nt"
        Requires-Dist: distlib<1,>=0.3.7
        Requires-Dist: jsonschema-specifications>=2023.03.6
        Requires-Dist: jaraco.classes
        Requires-Dist: jaraco.packages ; extra == "testing"
        Requires-Dist: mdurl~=0.1 ; extra == "ext"
        Requires-Dist: packaging >= 19.0
        Requires-Dist: poetry (>=1.5.0,<2.0.0)
        Requires-Dist: poetry-core (>=1.6.0,<2.0.0)
        Requires-Dist: pyproject_hooks
        Requires-Dist: SecretStorage (>=3.2) ; sys_platform == "linux"
        Requires-Dist: sphinx ~= 4.0 ; extra == "docs"
        Requires-Dist: sphinx-autodoc-typehints!=1.23.4,>=1.23; extra == 'docs'
    """
    pattern = re.compile(r'^([-.\w]+)(?: \(([^)]+)\)|([^;]+))?')
    #                       ^1------^      ^2----^   ^3----^
    
    def walk() -> t.Iterator[str]:
        with ropen(metadata_file) as f:
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
                # print(':v', line.rstrip())
                yield line[len(head) :].strip()
    
    for line in walk():
        if ';' in line:
            # e.g. 'Requires-Dist: toml; extra == "ext"'
            continue
        try:
            m = pattern.match(line)
            raw_name = m.group(1)
            raw_verspec = m.group(2) or m.group(3) or ''
            raw_verspec = raw_verspec.replace(' ', '')
        except AttributeError as e:
            print(':lv4', metadata_file, line, e)
            raise e
        name = norm.normalize_name(raw_name)
        verspecs = norm.normalize_version_spec(name, raw_verspec)
        yield name, verspecs


def analyze_records(record_file: str) -> t.Iterator[T.PathName]:
    records = loads(record_file, 'plain').splitlines()
    for line in records:
        path = fs.normpath(line.rsplit(',', 2)[0])
        if path.startswith('../'):
            # e.g. '../../../bin/dulwich'
            # TODO: currently we don't take account of this case.
            # print(':vs', 'discard external binary', path)
            continue
            # assert path.lstrip('./').startswith('bin/')
            # raise Exception(path)
        elif path.startswith('bin/'):
            path_name = 'bin/{}'.format(path[4:].split('/', 1)[0])
        else:
            path_name = path.split('/', 1)[0]
        yield path_name
