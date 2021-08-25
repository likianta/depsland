import re
from os.path import exists
from time import time

from lk_logger import lk
from lk_utils import dumps
from pkginfo import Wheel

from .data_struct import PackageInfo, Requirement
from .path_struct import pypi_struct
from .pip import default_pip
from .typehint import *
from .utils import find_best_matched_version, unzip_file


class LocalPyPI:
    UPDATE_FREQ = 60 * 60 * 24 * 7  # one week
    
    pip: TPip
    
    name_versions: TNameVersions
    locations: TLocationsIndex
    dependencies: TDependenciesIndex
    updates: TUpdates
    
    __circular_deps = []
    
    def __init__(self, pip: TPip):
        self.pip = pip
        a, b, c, d = pypi_struct.load_indexed_data()
        self.name_versions = a
        self.locations = b
        self.dependencies = c
        self.updates = d
    
    def get_all_dependencies(self, name_id, holder=None) -> list[TNameId]:
        if holder is None:
            holder = []
        for dep_name_id in self.dependencies[name_id]:
            if dep_name_id in holder:
                continue
            holder.append(dep_name_id)
            self.get_all_dependencies(dep_name_id, holder)
        return holder
    
    def get_locations(self, name_id) -> TLocations:
        return self.locations[name_id]
    
    def main(self, req: TRequirement):
        # if version doesn't in self.name_versions, or the version requests
        # latest but local repository is outdated, we should refresh local
        # repository.
        version = self._get_local_matched_version(req)
        if not version:
            for new_req in self._refresh_local_repo(req):
                self.main(new_req)
            version = self._get_local_matched_version(req, check_outdated=False)
            assert version
        
        req.set_fixed_version(version)
        name, version, name_id = req.name, req.version, req.name_id
        
        return PackageInfo(
            name=name, version=version, name_id=name_id,
            locations=self.locations[name_id],
            dependencies=self.dependencies[name_id]
        )
    
    def _get_local_matched_version(self, req, check_outdated=True):
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
        if req.name not in self.name_versions:
            return None
        if req.version_spec == 'latest':
            if check_outdated and self._is_outdated(req.name):
                return None
        version_list = self.name_versions[req.name]
        return find_best_matched_version(req.version_spec, version_list)
    
    def _is_outdated(self, name):
        if t := self.updates.get(name):
            if (time() - t) <= self.UPDATE_FREQ:
                return False
        return True
    
    def _refresh_local_repo(self, req: TRequirement):
        def finish_processing():
            self.__circular_deps.clear()
            self.updates[req.name] = int(time())
            return
        
        if not (path := self._download(req.raw_name, pypi_struct.downloads)):
            # current case: assert path == ''
            return finish_processing()
        
        # FIXME: '.tar.gz' suffix supports
        assert path.endswith('.whl'), (
            'This file type is not supported yet', path
        )
        
        whl = Wheel(path)
        req.set_fixed_version(whl.version)
        name, version, name_id = req.name, req.version, req.name_id
        
        # extract and update index
        loc = unzip_file(path, pypi_struct.mkdir(name_id))
        # try:
        #     loc = unzip_file(path, pypi_struct.mkdir(name_id))
        # except FileExistsError:  # TEST
        #     loc = f'{pypi_struct.extraced}/{name_id}'
        
        # update indexes
        self.name_versions[name].append(version)
        self.locations[name_id].append(loc)
        #   TODO: assign sole location instead of list[location] type
        for raw_name in whl.requires_dist:
            lk.logt('[D4831]', raw_name)
            #   e.g. 'cachecontrol[filecache] (>=0.12.4,<0.13.0)',
            #        'cachy (>=0.3.0,<0.4.0)', ...
            new_req = Requirement(raw_name.replace('(', '').replace(')', ''))
            
            # yielding new_req to the caller (`self.main`), the caller will
            # firstly handle it and update its related indexed data, then
            # continue to current thread.
            # be notice that if a circular dependency found, for example
            # package A depends on B but B (or B's dependencies) also depends
            # on A, a circular import error will be raised.
            if new_req.name in self.__circular_deps:
                raise Exception()
            else:
                self.__circular_deps.append(new_req.name)
                yield new_req
            
            version = find_best_matched_version(
                new_req.version_spec, self.name_versions[new_req.name]
            )
            new_req.set_fixed_version(version)
            self.dependencies[name_id].append(new_req.name_id)
        
        _sort_versions(self.name_versions[name])
        _sort_versions(self.dependencies[name_id])
        
        return finish_processing()
    
    def _download(self, raw_name, dst_dir):
        """
        Returns:
            Union[path, empty_string]
                path: new downloaded file path
                empty_string: the requested file already exists in local
        """
        # use quotes around `raw_name` because `raw_name` includes version
        # specifiers (like '>', '<', etc.) which should be wrapped when using
        # in shell. (https://pip.pypa.io/en/stable/cli/pip_install/#requirement
        # -specifiers)
        ret = self.pip.download(f'"{raw_name}"', dst_dir)
        r'''
            Sucessfully downloaded example:
                Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                Collecting lk-logger
                  Using cached .../lk_logger-3.6.3-py3-none-any.whl (11KB)
                Saved e:\...\lk_logger-3.6.3-py3-none-any.whl
                Successfully downloaded lk-logger
            File already exists:
                Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                Collecting lk-logger
                  File was already downloaded e:\downloads\lk_logger-3.6.3-py3-
                  none-any.whl
                Successfully downloaded lk-logger
        '''
        lk.logt('[D2054]', ret.replace('\n', '[\\n]'))
        # get name from ret info
        if new_file_matched := re.search(r'(?<=Saved ).+', ret):
            path = new_file_matched.group()
            assert exists(path)
            return path
        else:
            assert re.search(r'(?<=File was already downloaded ).+', ret)
            return ''
            # # TEST
            # return re.search(r'(?<=File was already downloaded ).+', ret).group()
    
    def save(self):
        for data, file in zip(
                (self.name_versions,
                 self.locations,
                 self.dependencies,
                 self.updates),
                pypi_struct.get_indexed_files()
        ):
            dumps(data, file)


def _sort_versions(versions: list[TVersion], reverse=True):
    """
    References:
        https://stackoverflow.com/questions/12255554/sort-versions-in-python/12255578
    """
    from distutils.version import StrictVersion
    versions.sort(key=lambda x: StrictVersion(x.split('-', 1)[-1]),
                  # `x` type is Union[TNameId, TVersion], for TNameId we need
                  # to split out the name part.
                  reverse=reverse)
    return versions


local_pypi = LocalPyPI(default_pip)

__all__ = ['local_pypi']
