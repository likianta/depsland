import os
import re
from time import time

from lk_logger import lk
from lk_utils import dumps, send_cmd
from pkginfo import SDist, Wheel

from .data_struct import PackageInfo, Requirement
from .path_struct import pypi_struct
from .pip import default_pip
from .typehint import *
from .utils import find_best_matched_version, sort_versions, unzip_file


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
        else:
            lk.loga('found requirement in local repo', req)
        
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
        if req.version_spec == '*':
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
        
        path = self._download(req.raw_name, pypi_struct.downloads)
        
        if path.endswith('.whl'):
            pkg = Wheel(path)
        elif path.endswith('.tar.gz'):
            pkg = SDist(path)
        else:
            raise Exception('This file type is not recognized', path)
        
        req.set_fixed_version(pkg.version)
        name, version, name_id = req.name, req.version, req.name_id
        
        if version in self.name_versions[name]:
            lk.loga('local repo satisfies requirement '
                    '(refresh local time only)')
            return finish_processing()
        
        # extract and update index
        try:
            loc = pypi_struct.mkdir(name_id)
            unzip_file(path, pypi_struct.mkdir(name_id))
        except FileExistsError:
            loc = pypi_struct.extraced + '/' + name_id
        
        # update indexes
        # note: use lazy updation. i.e. donot update indexed data (`self
        # .name_versions`, `self.locations`, `self.dependencies`) immediately,
        # create a new temp var to hold the upcoming data, then self indexed
        # data extends the var.
        # why: because the dependencies processing is not stable in current
        # depsland version, it ofter occurs unexpected errors (e.g. downloading
        # timeout, complicated uncovered version comparisons, etc.), if we
        # update indexed data in processing, it maybe crashed and depsland will
        # try to save an uncomplete data to local, which is harmful to the next
        # time restarting.
        deps = []
        for raw_name in pkg.requires_dist:
            lk.logt('[D4831]', raw_name)
            #   e.g. 'cachecontrol[filecache] (>=0.12.4,<0.13.0)',
            #        'cachy (>=0.3.0,<0.4.0)', ...
            new_req = Requirement(raw_name)
            lk.loga(f'got new requirement "{new_req}" from "{req}"')
            
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
            deps.append(new_req.name_id)

        self.name_versions[name].append(version)
        self.locations[name_id].append(loc)
        #   FIXME: assign sole location instead of list[location] type
        self.dependencies[name_id].extend(deps)
        
        sort_versions(self.name_versions[name])
        # sort_versions(self.dependencies[name_id])
        
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
        lk.loga('downloading package (this takes a few seconds/minutes...)',
                raw_name)
        ret = send_cmd(self.pip.get_pip_cmd(
            'download', f'"{raw_name}"', f'-d "{dst_dir}"', '--no-deps'
        ))
        # ret = self.pip.download(f'"{raw_name}"', dst_dir)
        # lk.logt('[D2054]', ret.replace('\n', '[\\n]'))
        r'''
            Sucessfully downloaded example:
                Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                Collecting lk-logger
                  Using cached .../lk_logger-3.6.3-py3-none-any.whl (11KB)
                Saved e:\...\lk_logger-3.6.3-py3-none-any.whl
                Successfully downloaded lk-logger
            File already exists example:
                Looking in indexes: https://pypi.tuna.tsinghua.edu.cn/simple
                Collecting lk-logger
                  File was already downloaded e:\downloads\lk_logger-3.6.3-py3-
                  none-any.whl
                Successfully downloaded lk-logger
        '''
        # get name from ret info
        if x := re.search(r'(?<=Saved ).+', ret):
            path = x.group()
            lk.loga('new file downloaded', os.path.basename(path))
        elif y := re.search(r'(?<=File was already downloaded ).+', ret):
            path = y.group()
            lk.loga('file already exists', os.path.basename(path))
        else:
            raise Exception('Unknown returned value', ret)
        # assert exists(path)
        return path
    
    def save(self):
        for data, file in zip(
                (self.name_versions,
                 self.locations,
                 self.dependencies,
                 self.updates),
                pypi_struct.get_indexed_files()
        ):
            dumps(data, file)


local_pypi = LocalPyPI(default_pip)

__all__ = ['local_pypi']
