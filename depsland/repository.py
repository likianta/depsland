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
    
    def main(self, req: TRequirement):
        name = req.name
        if self._is_outdated(name) or find_best_matched_version(
                req.version, self.name_versions[name]
        ) is None:
            for new_req in self._refresh_local_repo(req):
                self.main(new_req)
        
        version = find_best_matched_version(
            req.version, self.name_versions[name]
        )
        return PackageInfo(
            name=name, version=version,
            locations=self.locations[name],
            dependencies=self.dependencies[name]
        )
    
    def get_all_dependencies(self, name_id) -> TNameId:
        yield name_id
        for i in self.dependencies[name_id]:
            yield i
            yield from self.get_all_dependencies(i)
            
    def get_locations(self, name_id) -> TLocations:
        return self.locations[name_id]
    
    def _is_outdated(self, name):
        if t := self.updates.get(name):
            if (time() - t) <= self.UPDATE_FREQ:
                return False
        return True
    
    def _refresh_local_repo(self, req: TRequirement):
        path = self._download(req.raw_name)
        
        # analyse path
        if not path.endswith('.whl'):
            raise NotImplemented('This file type is not supported yet', path)
        
        whl = Wheel(path)
        req.version = whl.version  # update req.version
        name, version, name_id = req.name, req.version, req.name_id
        
        if (x := self.name_versions.get(name)) and version in x:
            # this means the new downloaded file is already existed and has
            # been indexed
            self.updates[name] = time()
            return
            
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
        
        self.updates[name] = time()
    
    def _download(self, raw_name):
        ret = self.pip.download(raw_name)
        r''' e.g.
            Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
            Collecting lk-logger
              Using cached https://.../lk_logger-3.6.3-py3-none-any.whl (11 kB)
            Saved e:\...\lk_logger-3.6.3-py3-none-any.whl
            Successfully downloaded lk-logger
        '''
        # get name from ret info
        path = re.search(r'(?<=Saved ).+', ret).group()  # type: str
        assert exists(path)
        return path
