import re
import typing as t
from os.path import exists

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

from . import utils
from .normalization import T as T0
from .normalization import VersionSpec
from .normalization import normalize_name
from .paths import pypi as pypi_paths
from .pip import Pip
from .pip import pip as _default_pip
from .utils import verspec

__all__ = ['T', 'pypi']


class T:
    Name = T0.Name
    NameId = str  # f'{Name}-{FixedVersion}'
    Path = str
    Pip = Pip
    Version = T0.Version
    VersionSpecs = t.Iterable[VersionSpec]
    
    Location = Path
    Packages = t.Dict[Name, VersionSpecs]
    
    # indexes
    Dependencies = t.Dict[NameId, t.List[NameId]]
    Name2Versions = t.Dict[Name, t.List[Version]]
    #   t.List[...]: a sorted versions list, from new to old.
    NameId2Paths = t.Dict[Version, t.Tuple[Path, Path]]
    #   t.List[...]: tuple[downloaded_path, installed_path]
    Updates = t.Dict[Name, int]


class LocalPyPI:
    pip: T.Pip
    
    name_2_versions: T.Name2Versions
    name_id_2_paths: T.NameId2Paths
    # locations: T.LocationsIndex
    dependencies: T.Dependencies
    updates: T.Updates
    
    # # update_freq = 60 * 60 * 24 * 7  # one week
    update_freq = -1
    
    def __init__(self, pip=_default_pip):
        self.pip = pip
        self._load_index()
        # atexit.register(self.save_index)
    
    def _load_index(self):
        self.name_2_versions = loads(pypi_paths.name_2_versions)
        self.name_id_2_paths = loads(pypi_paths.name_id_2_paths)
        # self.locations = loads(pypi_paths.locations)
        self.dependencies = loads(pypi_paths.dependencies)
        self.updates = loads(pypi_paths.updates)
    
    def save_index(self) -> None:
        dumps(self.name_2_versions, pypi_paths.name_2_versions)
        dumps(self.name_id_2_paths, pypi_paths.name_id_2_paths)
        dumps(self.dependencies, pypi_paths.dependencies)
        dumps(self.updates, pypi_paths.updates)
    
    # -------------------------------------------------------------------------
    
    def download(
            self,
            packages: T.Packages,
            include_dependencies=False,
    ) -> t.Iterator[t.Tuple[T.Name, T.Version, T.Path]]:
        # noinspection PyTypeChecker
        for name, specs in packages.items():
            if name in self.name_2_versions:
                proper_existed_version = verspec.find_proper_version(
                    *specs, candidates=self.name_2_versions[name]
                )
                if proper_existed_version:
                    name_id = f'{name}-{proper_existed_version}'
                    filepath = self.name_id_2_paths[name_id][0]
                    print(':v', 'found package from local', name_id)
                    yield name, proper_existed_version, filepath
                    
                    if include_dependencies:
                        for nid in self.dependencies[name_id]:
                            a, b = nid.split('-', 1)
                            yield a, b, self.name_id_2_paths[nid][0]
                    continue
            
            # start downloading
            print('download package via pip', name)
            dependencies: t.List[T.NameId] = []
            source_name = name
            source_name_id = ''
            # del name  # variable `name` is released
            for filepath, is_new in self._download(
                    source_name, specs, include_dependencies
            ):
                filename = fs.filename(filepath)
                #   e.g. 'PyYAML-6.0-cp310-cp310-macosx_10_9_x86_64.whl'
                #        'lk-logger-4.0.7.tar.gz'
                #        'aliyun-python-sdk-2.2.0.zip'
                if filename.endswith('.whl'):
                    name, version, _ = filename.split('-', 2)
                else:
                    name, version = filename.rsplit('-', 1)
                name = normalize_name(name)  # e.g. 'PyYAML' -> 'pyyaml'
                name_id = f'{name}-{version}'
                print(':v', 'downloaded package via pip', name_id)
                
                if is_new:
                    self.name_2_versions[name].insert(0, version)
                    self.name_id_2_paths[name_id] = (filepath, '')
                    yield name, version, filepath
                # else:
                #     assert version in self.name_2_versions[name]
                #     assert name_id in self.version_2_path
                
                if name == source_name:
                    source_name_id = name_id
                else:
                    dependencies.append(name_id)
            assert source_name_id
            self.dependencies[source_name_id] = dependencies
    
    def install(self, packages: T.Packages, include_dependencies=False) \
            -> t.Iterator[T.NameId]:
        for name, version, downloaded_path in self.download(
                packages, include_dependencies
        ):
            name_id = f'{name}-{version}'
            installed_path = self.name_id_2_paths[name_id][1]
            if installed_path:
                yield name_id
                continue
            else:
                installed_path = '{}/{}/{}'.format(
                    pypi_paths.installed,
                    name,
                    version
                )
                self.pip.run(
                    'install', downloaded_path,
                    '--no-deps', '--no-index',
                    ('-t', installed_path),
                    ('--find-links', pypi_paths.downloads),
                )
                self.name_id_2_paths[name_id] = \
                    (downloaded_path, installed_path)
                yield name_id
    
    def linking(self, name_ids: t.Iterable[T.NameId], dst_dir: T.Path) -> None:
        print(':d', f'linking environment packages to {dst_dir}')
        print(':l', name_ids)
        
        for nid in name_ids:
            installed_path = self.name_id_2_paths[nid][1]
            assert exists(installed_path)
            try:
                utils.mklinks(installed_path, dst_dir, force=False)
            except FileExistsError:
                utils.mergelinks(installed_path, dst_dir, overwrite=None)
    
    # -------------------------------------------------------------------------
    
    def _download(
            self, name: T.Name, specs: T.VersionSpecs,
            include_dependencies=False,
    ) -> t.Iterator[t.Tuple[T.Path, bool]]:
        """
        return: iter[tuple[abspath_of_whl_or_tar_file, is_new_file]]
        """
        response = self.pip.download(
            name=name,
            version=','.join(x.spec for x in specs),
            dest=pypi_paths.downloads,
            no_deps=not include_dependencies,
        )
        ''' e.g. 1:
                Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                ...
                  Saved <abspath>
            e.g. 2:
                Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                ...
                  File was already downloaded <abspath>
        '''
        pattern1 = re.compile(r'(?<=File was already downloaded ).+')
        pattern2 = re.compile(r'(?<=Saved ).+')
        for m in pattern1.finditer(response):
            yield m.group(), False
        for m in pattern2.finditer(response):
            yield m.group(), True
    
    def _extract_dependencies(self, whl_or_tar_file: T.Path) -> T.VersionSpecs:
        pass


pypi = LocalPyPI()
