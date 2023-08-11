import re
import sys
import typing as t
from collections import defaultdict

from lk_utils import fs
from lk_utils import loads
from lk_utils import run_cmd_args
from lk_utils.read_and_write import ropen

from ... import normalization as norm
from ...utils import get_file_hash
from ...utils import verspec


# noinspection PyTypedDict
class T:
    ExactVersion = str
    NameId = str  # str['{name}-{version}']
    PkgName = str
    TopName = str  # union[dir_name, file_name, bin_name]
    
    PkgInfo = t.TypedDict(
        'PkgInfo',
        {
            'name_id'     : NameId,
            'version'     : ExactVersion,
            'hash'        : str,
            'url'         : str,
            'paths'       : t.Iterable[TopName],
            'dependencies': t.List[NameId],
        },
    )
    
    DepsMap = t.Dict[PkgName, PkgInfo]


class TargetVenvIndex:
    def __init__(self, working_dir: str):
        self._working_dir = working_dir
        self.root = self.get_target_venv_root()
        self.all_deps = self.build_deps_map(self.root)
    
    def get_target_venv_root(self) -> str:
        poetry_cli = (sys.executable, '-m', 'poetry')
        return fs.normpath(
            run_cmd_args(
                poetry_cli, 'env', 'info', '--path', '-C', self._working_dir
            )
        )
    
    # -------------------------------------------------------------------------
    
    def build_deps_map(self, root: str) -> T.DepsMap:
        map_: T.DepsMap = {}  # noqa
        
        for dname, dpath in self._find_dist_info_dirs(root):
            name, ver = norm.split_dirname_of_dist_info(dname)
            url = self._get_custom_url(dpath)
            
            record_file = f'{dpath}/RECORD'
            assert fs.exists(record_file)
            
            record_hash = get_file_hash(record_file)
            top_names = set(self._analyze_records(record_file))
            
            # noinspection PyTypeChecker
            map_[name] = {
                'name_id'     : f'{name}-{ver}',
                'version'     : ver,
                'hash'        : record_hash,
                'url'         : url or '',
                'paths'       : sorted(top_names),
                'dependencies': [],
            }
        
        relations = self.analyze_deps_relations(root, map_)
        for name, sub_name_ids in relations.items():
            map_[name]['dependencies'].extend(sorted(sub_name_ids))
        
        return map_
    
    def analyze_deps_relations(self, root: str, deps_map: T.DepsMap):
        out = defaultdict(set)
        for dname, dpath in self._find_dist_info_dirs(root):
            parent_name, _ = norm.split_dirname_of_dist_info(dname)
            assert parent_name in deps_map
            
            metadata_file = f'{dpath}/METADATA'
            if fs.exists(metadata_file):
                for sub_name, verspecs in self._analyze_metadata(metadata_file):
                    if sub_name in deps_map:
                        exact_version = deps_map[sub_name]['version']
                        assert (
                            verspec.find_proper_version(
                                *verspecs, candidates=(exact_version,)
                            )
                            == exact_version
                        )
                        sub_name_id = f'{sub_name}-{exact_version}'
                        out[parent_name].add(sub_name_id)
                    else:
                        print(':lv4', deps_map, sub_name)
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
    ) -> t.Iterator[t.Tuple[T.PkgName, t.Iterator[verspec.VersionSpec]]]:
        pattern = re.compile(r'([-\w]+)(?: \(([^)]+)\))?')
        
        #                      ^~~~~~~1      ^~~~~~2
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
    def _analyze_records(file: str) -> t.Iterator[T.TopName]:
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
