import os
import re
import typing as t

from lk_utils import fs

from .index import Index
from .index import T as T0
from .. import normalization as norm
from ..paths import pypi as pypi_paths
from ..pip import Pip
from ..pip import pip as _default_pip
from ..utils import get_updated_time
from ..utils import verspec
from ..venv import link_venv

__all__ = ['T', 'pypi']


class T(T0):
    Pip = Pip
    VersionSpecs = t.Iterable[norm.VersionSpec]
    Packages = t.Dict[T0.Name, VersionSpecs]


class LocalPyPI(Index):
    pip: T.Pip
    
    def __init__(self, pip=_default_pip):
        super().__init__()
        self.pip = pip
    
    # -------------------------------------------------------------------------
    # main methods
    
    def download(
            self,
            packages: T.Packages,
            include_dependencies=False,
            _check_local_existed_versions=True,
    ) -> t.Iterator[t.Tuple[T.Name, T.Version, T.Path]]:
        
        def get_downloaded_path(name_id: str) -> T.Path:
            return '{}/{}'.format(
                pypi_paths.root, self.name_id_2_paths[name_id][0]
            )
        
        for name, specs in packages.items():
            if _check_local_existed_versions:
                if name in self.name_2_versions:
                    proper_existed_version = verspec.find_proper_version(
                        *specs, candidates=self.name_2_versions[name]
                    )
                    if proper_existed_version:
                        name_id = f'{name}-{proper_existed_version}'
                        filepath = get_downloaded_path(name_id)
                        print(':v', 'found package from local', name_id)
                        yield name, proper_existed_version, filepath
                        
                        if include_dependencies:
                            for nid in self.dependencies[name_id]['resolved']:
                                a, b = nid.split('-', 1)
                                yield a, b, get_downloaded_path(nid)
                            yield from self._download_unresolved_part(name_id)
                        continue
                    else:
                        print('cannot find proper version in local index, '
                              'will fallback to default pip download', name)
            
            # start downloading
            print('download package via pip', name)
            dependencies: t.List[T.NameId] = []  # the resolved part
            source_name = name
            source_name_id = ''
            # del name  # variable `name` is not used below.
            for filepath, is_new in self._download(
                    source_name, specs, include_dependencies
            ):
                filename = fs.filename(filepath)
                # extract name and version info from filename.
                name, version = norm.filename_2_name_version(filename)
                name_id = f'{name}-{version}'
                print(':v', 'downloaded package via pip', name_id)
                
                if is_new:
                    # FIXME: insert to a proper position.
                    self.name_2_versions[name].insert(0, version)
                if name_id not in self.name_id_2_paths:
                    # if is_new: the name_id definitely not in ...;
                    # if not is_new: it is sometimes possible that not in
                    #   self.name_id_2_paths. e.g. when external caller has
                    #   downloaded some packages via custom pypi site.
                    self.name_id_2_paths[name_id] = (
                        fs.relpath(filepath, pypi_paths.root),
                        fs.relpath('{}/{}/{}'.format(
                            pypi_paths.installed, name, version
                        ), pypi_paths.root)
                    )
                    print(':v', 'make dir', f'{pypi_paths.installed}/{name}')
                    fs.make_dir(f'{pypi_paths.installed}/{name}')
                yield name, version, filepath
                # else:
                #     assert version in self.name_2_versions[name]
                #     assert name_id in self.version_2_path
                
                if name == source_name:
                    source_name_id = name_id
                else:
                    dependencies.append(name_id)
            assert source_name_id
            self.dependencies[source_name_id]['resolved'].extend(dependencies)
    
    def install(self, packages: T.Packages, include_dependencies=False) \
            -> t.Iterator[T.NameId]:
        """
        yield note:
            1. the yielded name_ids may duplicate.
            2. the yielded sequence may be useful (for example to deal with the
                conflict of dependencies). so don't use `set()` to remove
                duplicates, use `list(dict.fromkeys())` instead.
                (ref: https://www.w3schools.com/python/python_howto_remove
                _duplicates.asp)
        """
        
        def get_installed_path(name_id: str) -> t.Tuple[T.Path, bool]:
            path = '{}/{}'.format(
                pypi_paths.root, self.name_id_2_paths[name_id][1]
            )
            return path, os.path.exists(path)
        
        for name, version, downloaded_path in self.download(
                packages, include_dependencies
        ):
            name_id = f'{name}-{version}'
            installed_path, exist = get_installed_path(name_id)
            if not exist:
                print(':v', 'make dir', installed_path)
                fs.make_dir(installed_path)
                self.pip.run(
                    'install', downloaded_path,
                    '--no-deps', '--no-index',
                    ('-t', installed_path),
                    ('--find-links', pypi_paths.downloads),
                )
            yield name_id
    
    @staticmethod
    def linking(name_ids: t.Iterable[T.NameId], dst_dir: T.Path) -> None:
        print(':d', f'linking environment packages to {dst_dir}')
        print(':l', name_ids)
        link_venv(name_ids, dst_dir)
    
    # -------------------------------------------------------------------------
    # side methods
    
    def add_to_index(
            self,
            downloaded_package_file: str,
            download_dependencies=False
    ) -> None:
        filename = fs.filename(downloaded_package_file)
        name, version = norm.filename_2_name_version(filename)
        name_id = f'{name}-{version}'
        
        path0 = fs.normpath(downloaded_package_file, True)
        path1 = '{}/{}'.format(pypi_paths.downloads, filename)
        path2 = '{}/{}/{}'.format(pypi_paths.installed, name, version)
        
        def fill_local_dirs() -> None:
            if path0 != path1:
                fs.copy_file(path0, path1)
            if not os.path.exists(path2):
                print(':v', f'perform local pip install on {name_id}')
                fs.make_dirs(path2)
                self.pip.run(
                    'install', path1, ('-t', path2),
                    '--no-deps', '--no-index',
                )
        
        def add_to_indexes() -> None:
            self.name_2_versions[name].insert(0, version)
            
            self.name_id_2_paths[name_id] = (
                fs.relpath(path1, pypi_paths.root),
                fs.relpath(path2, pypi_paths.root),
            )
            
            for (a, b), is_name_id in self._find_dependencies(name_id):
                if is_name_id:
                    self.dependencies[name_id]['resolved'].append(f'{a}-{b}')
                else:
                    self.dependencies[name_id]['unresolved'][a] = tuple(
                        norm.normalize_version_spec(a, b)
                    )
            
            if name not in self.updates:
                self.updates[name] = get_updated_time(path0)
            elif (x := get_updated_time(path0)) > self.updates[name]:
                self.updates[name] = x
        
        if name_id not in self.name_id_2_paths:
            fill_local_dirs()
            add_to_indexes()
        # else: assert name_id in all indexes...
        
        if download_dependencies and self.dependencies[name_id]['unresolved']:
            print(f'predownload dependencies for {name_id}')
            tuple(self._download_unresolved_part(name_id))
    
    # -------------------------------------------------------------------------
    # general
    
    def exists(self, name_or_id: t.Union[T.Name, T.NameId]) -> bool:
        if '-' not in name_or_id or name_or_id.endswith('-'):
            name = name_or_id.rstrip('-')
            return name in self.name_2_versions
        else:
            name_id = name_or_id
            return name_id in self.name_id_2_paths
    
    @staticmethod
    def split(name_id: T.NameId) -> t.Tuple[T.Name, T.Version]:
        return name_id.split('-', 1)  # noqa
    
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
    
    def _download_unresolved_part(
            self, name_id: T.NameId
    ) -> t.Iterator[t.Tuple[T.Name, T.Version, T.Path]]:
        if x := self.dependencies[name_id]['unresolved']:
            yield from self.download(
                x,
                include_dependencies=True,
                _check_local_existed_versions=False,
            )
            x.clear()
    
    def _find_dependencies(self, name_id: str) -> t.Iterator[T.NameId]:
        from .insight import _analyse_metadata_1
        dir0 = '{}/{}'.format(
            pypi_paths.root,
            self.name_id_2_paths[name_id][1]
        )
        for name in os.listdir(dir0):
            if name.endswith('.dist-info'):
                dir1 = f'{dir0}/{name}'
                if os.path.exists(x := f'{dir1}/METADATA'):
                    yield from _analyse_metadata_1(x, self.name_2_versions)
                break
        else:
            raise Exception(f'cannot find dist-info for {name_id}')


pypi = LocalPyPI()
