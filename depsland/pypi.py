import re
import typing as t
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads
from os.path import exists
from . import utils
from .normalization import T as T0
from .normalization import VersionSpec
from .normalization import normalize_name
from .paths import pypi as pypi_paths
from .pip import Pip
from .pip import pip as _default_pip
from .utils import verspec

__all__ = ['pypi']


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
                    request=specs,
                    candidates=self.name_2_versions[name]
                )
                if proper_existed_version:
                    name_id = f'{name}-{proper_existed_version}'
                    filepath = self.name_id_2_paths[name_id][0]
                    yield name, proper_existed_version, filepath
                    
                    if include_dependencies:
                        for nid in self.dependencies[name_id]:
                            a, b = nid.split('-', 1)
                            yield a, b, self.name_id_2_paths[nid][0]
                    continue
            
            # start downloading
            dependencies: t.List[T.NameId] = []
            source_name = name
            source_name_id = ''
            # del name  # variable `name` is released
            for filepath, is_new in self._download(
                    source_name, specs, include_dependencies
            ):
                filename = fs.filename(filepath)
                #   e.g. 'PyYAML-6.0-cp310-cp310-macosx_10_9_x86_64.whl'
                name, version, _ = filename.split('-', 2)
                name = normalize_name(name)  # e.g. 'PyYAML' -> 'pyyaml'
                name_id = normalize_name(f'{name}-{version}')
                
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
    
    # -------------------------------------------------------------------------
    # DELETE BELOW
    
    ''' 
    def analyse_requirement(self, req: T.Requirement) -> T.PackageInfo:
        # if version doesn't in self.name_versions, or the version requests
        # latest but local repository is outdated, we should refresh local
        # repository.
        version = self._get_local_matched_version(req)
        if version:
            print('found requirement in local repo', req)
            req.set_fixed_version(version)
        else:
            print('request requirement from pip (online)', req)
            req = self._refresh_local_repo(req)
        
        name, version, name_id = req.name, req.version, req.name_id
        
        return PackageInfo(
            name=name, version=version, name_id=name_id,
            dependencies=self.dependencies[name_id]
        )
    
    def get_all_dependencies(
            self,
            name_id: T.NameId,
            holder: t.Optional[t.List[T.NameId]] = None
    ) -> t.List[T.NameId]:
        if holder is None:
            holder = []
        for dep_name_id in self.dependencies[name_id]:
            if dep_name_id in holder:
                continue
            holder.append(dep_name_id)
            self.get_all_dependencies(dep_name_id, holder)
        return holder
    
    @staticmethod
    def get_location(name_id: T.NameId) -> T.Location:
        out = pypi_paths.extracted + '/' + name_id
        assert os.path.exists(out)  # this dir is generated by
        #   `self._refresh_local_repo:MARK@20210918100418`
        return out
    
    def _get_local_matched_version(
            self,
            req: T.Requirement,
            check_outdated=True
    ):
        """
        
        Notice:
            If returns None, it means:
                a) the requested version doesn't exist in `self.name_versions`.
                b) the version requests latest but the local repository is
                   outdated.
            In case (a) we know that the downloading session is required; in
            case (b) we don't know whether it already exists.
            So the downloader should check whether an incoming 'latest' version
            exists to avoid saving an existed verison which may cause a
            FileExistsError.
        """
        if req.name not in self.name_2_versions:
            return None
        if req.version_spec == LATEST:
            if check_outdated and self._is_outdated(req.name):
                return None
        version_list = self.name_2_versions[req.name]
        return find_best_matched_version(req.version_spec, version_list)
    
    def _is_outdated(self, name: T.Name) -> bool:
        if self.update_freq == -1:
            return False  # never outdated
        if t := self.updates.get(name):
            if (time() - t) <= self.update_freq:
                return False
        return True
    
    def _refresh_local_repo(self, req: T.Requirement) -> T.Requirement:
        _req = req
        
        deps = {}
        available_namespace = {}
        
        for path in self._download(req.raw_name, pypi_paths.downloads):
            if path.endswith(('.whl', '.zip')):
                pkg = Wheel(path)
            elif path.endswith(('.tar.gz', '.tar')):
                pkg = SDist(path)
            else:
                raise Exception('This file type is not recognized', path)
            
            req = Requirement(pkg.name, pkg.version)
            name, version, name_id = req.name, req.version, req.name_id
            
            available_namespace[name] = version
            
            # self.updates
            self.updates[name] = int(time())
            
            # self.name_versions
            if version in self.name_2_versions[name]:
                print('local repo satisfies requirement', name_id)
                continue
            else:
                self.name_2_versions[name].append(version)
                sort_versions(self.name_2_versions[name])
            
            try:  # MARK: 20210918100418
                loc = '{}/{}'.format(pypi_paths.extracted, name_id)
                if not os.path.exists(loc):
                    os.mkdir(loc)
            except FileExistsError:
                pass
            else:
                ziptool.unzip_file(path, loc)
            
            # self.dependencies
            deps[name_id] = pkg.requires_dist
            #   pkg.requires_dist: e.g. 'cachecontrol[filecache] (>=0.12.4,
            #       <0.13.0)', 'cachy (>=0.3.0,<0.4.0)', ...
        
        assert _req.name in available_namespace, (
            _req, available_namespace
        )
        _req.set_fixed_version(available_namespace[_req.name])
        
        # noinspection PyTypeChecker
        for name_id, requires_dist in deps.items():
            for raw_name in requires_dist:
                # # excluded names
                # if re.search(r'\bextra\b *==', raw_name):
                #     print('exclude extra package', raw_name)
                #     continue
                
                dep = Requirement(raw_name)
                
                if dep.name not in available_namespace:
                    # it means this dep is an invalid package (authorized by
                    # pip download)
                    print('invalid package recorded in requires_dist but not '
                          'downloaded by pip-download', dep.raw_name)
                    continue
                
                version = available_namespace[dep.name]
                dep.set_fixed_version(version)
                self.dependencies[name_id].append(dep.name_id)
        
        return _req
    
    def _download_one(self, name: T.Name, version: str, dst_dir: T.Path) -> str:
        """
        args:
            version: a version includes a version spec, e.g. '>=1.0.0'
                (https://pip.pypa.io/en/stable/cli/pip_install/#requirement
                -specifiers)
                
        returns: str path_or_empty
            if path returned, it means a new package is requested to download.
            if empty, it means the requested package already exists in local.
        """
        reponse = self.pip.download(name, version, dst_dir, no_deps=True)
        """ e.g. 1:
                Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                ...
                  Saved <abspath>
            e.g. 2:
                Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                ...
                  File was already downloaded <abspath>
        """
        pattern1 = re.compile(r'(?<=Saved ).+')
        pattern2 = re.compile(r'(?<=File was already downloaded ).+')
        if m := pattern1.search(reponse):
            return m.group()
        elif pattern2.search(reponse):
            return ''
        else:
            raise Exception(reponse)
    '''


pypi = LocalPyPI()
