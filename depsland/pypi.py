import re
from os.path import exists
from time import time

from pkginfo import Wheel

from .struct import PackageInfo, Requirement
from .typehint import *
from .utils import unzip_file
from .venv_struct import pypi_struct
from .version_comp import find_best_matched_version


class LocalPyPI:
    UPDATE_FREQ = 60 * 60 * 24 * 7  # one week
    
    pip: TPip
    
    name_versions: TNameVersions
    locations: TLocationsIndex
    dependencies: TDependenciesIndex
    updates: TUpdates
    
    def __init__(self, pip: TPip):
        self.pip = pip
        a, b, c, d = pypi_struct.load_index_data()
        self.name_versions = a
        self.locations = b
        self.dependencies = c
        self.updates = d
    
    def get_all_dependencies(self, name_id, holder=None) -> list[TNameId]:
        if holder is None:
            holder = []
        holder.append(name_id)
        for i in self.dependencies[name_id]:
            if i in holder:
                continue
            self.get_all_dependencies(i, holder)
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
        
        # update req info
        req.version = version
        name, version, name_id = req.name, req.version, req.name_id
        
        return PackageInfo(
            name=name, version=version, name_id=name_id,
            locations=self.locations[name],
            dependencies=self.dependencies[name]
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
        if req.version == 'latest':
            if check_outdated and self._is_outdated(req.name):
                return None
            else:
                return self.name_versions[req.version]
        if not (versions := self.name_versions.get(req.version)):
            return None
        return find_best_matched_version(req.version, versions)
    
    def _is_outdated(self, name):
        if t := self.updates.get(name):
            if (time() - t) <= self.UPDATE_FREQ:
                return False
        return True
    
    def _refresh_local_repo(self, req: TRequirement):
        def finish_processing():
            self.updates[req.name] = time()
            return
        
        if not (path := self._download(req.raw_name, pypi_struct.downloads)):
            return finish_processing()
        
        # FIXME: '.tar.gz' suffix supports
        assert path.endswith('.whl'), (
            'This file type is not supported yet', path
        )
        
        whl = Wheel(path)
        req.version = whl.version  # update req.version
        name, version, name_id = req.name, req.version, req.name_id
        
        # extract and update index
        loc = unzip_file(whl, pypi_struct.mkdir(name_id))
        
        # update indexes
        self.name_versions[name] = version
        self.locations[name_id].append(loc)
        #   TODO: assign sole location instead of list[location] type
        for raw_name in whl.requires_dist:
            #   e.g. ['cachecontrol[filecache] (>=0.12.4,<0.13.0)',
            #         'cachy (>=0.3.0,<0.4.0)', ...]
            req = Requirement(raw_name)
            self.dependencies[name_id].append(req.name_id)
            yield req
        
        return finish_processing()
    
    def _download(self, raw_name, dst_dir):
        """
        Returns:
            Union[path, empty_string]
                path: new downloaded file path
                empty_string: the requested file already exists in local
        """
        ret = self.pip.download(raw_name, dst_dir)
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
        # get name from ret info
        if new_file_matched := re.search(r'(?<=Saved ).+', ret):
            path = new_file_matched.group()
            assert exists(path)
            return path
        else:
            assert re.search(r'(?<=File was already downloaded ).+', ret)
            return ''
