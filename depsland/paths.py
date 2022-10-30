"""
ref: ~/docs/project-structure.md
"""
import os
from collections import defaultdict
from lk_utils import dumps
from lk_utils import fs
from os.path import dirname
from os.path import exists

__all__ = [
    'apps', 'conf', 'oss', 'project', 'pypi', 'python', 'temp',
]

_CURR_DIR = fs.normpath(dirname(__file__), force_abspath=True)
_PROJ_DIR = fs.normpath(dirname(_CURR_DIR))
_IS_WINDOWS = os.name == 'nt'


class Project:
    root = f'{_PROJ_DIR}'
    # below attrs follow alphabetical order
    apps = f'{root}/apps'
    # cache = f'{root}/cache'
    conf = f'{root}/conf'
    project = f'{root}'
    pypi = f'{root}/pypi'
    python = f'{root}/python'
    temp = f'{root}/temp'


# -----------------------------------------------------------------------------

class Apps:
    root = f'{_PROJ_DIR}/apps'
    venv = f'{root}/.venv'
    _history_versions = f'{root}/{{appid}}/.history_versions.json'
    _packages = f'{root}/.venv/{{appid}}/packages'
    
    def get_history_versions(self, appid: str) -> str:
        return self._history_versions.format(appid=appid)
    
    def make_packages(self, appid: str, clear_exists=False) -> str:
        packages = self._packages.format(appid=appid)
        if exists(packages):
            if clear_exists:
                fs.remove_tree(packages)
                os.mkdir(packages)
        else:
            os.makedirs(packages)
        return packages


class Conf:
    root = f'{_PROJ_DIR}/conf'
    depsland = f'{root}/depsland.yaml'
    oss_client = f'{root}/oss_client.yaml'
    oss_server = f'{root}/oss_server.yaml'


class Oss:
    root = 'apps'
    assets: str
    manifest: str
    _appid: str = ''
    
    def set_appid(self, appid: str) -> 'Oss':
        self._appid = appid
        return self
    
    def __str__(self):
        assert self._appid
        return f'<oss://depsland/apps/{self._appid}>'
    
    @property
    def assets(self) -> str:
        assert self._appid
        return f'{self.root}/{self._appid}/assets'
    
    @property
    def manifest(self) -> str:
        assert self._appid
        return f'{self.root}/{self._appid}/manifest.pkl'


class PyPI:
    root = f'{_PROJ_DIR}/pypi'
    
    cache = f'{root}/cache'
    downloads = f'{root}/downloads'
    # extracted = f'{root}/extracted'
    index = f'{root}/index'
    installed = f'{root}/installed'
    
    dependencies = f'{root}/index/dependencies.pkl'
    # locations = f'{root}/index/locations.pkl'
    name_2_versions = f'{root}/index/name_2_versions.pkl'
    name_id_2_paths = f'{root}/index/name_id_2_paths.pkl'
    updates = f'{root}/index/updates.pkl'
    
    def __init__(self):
        # TODO: move this to `depsland setup` stage.
        if not exists(self.index):
            os.mkdir(self.index)
            dumps(defaultdict(list), self.dependencies)
            dumps(defaultdict(list), self.name_2_versions)
            # dumps(defaultdict(lambda : ('', '')), self.name_id_2_paths)
            # dumps(defaultdict(lambda : 0), self.updates)
            #   FIXME: local lambda cannot be pickled.
            dumps({}, self.name_id_2_paths)
            dumps({}, self.updates)


class Python:
    root = f'{_PROJ_DIR}/python'
    if _IS_WINDOWS:
        pip = f'{root}/Scripts/pip.exe'
        python = f'{root}/python.exe'
        site_packages = f'{root}/Lib/site-packages'
    else:
        pip = f'{root}/bin/pip'
        python = f'{root}/bin/python3.10'
        site_packages = f'{root}/lib/python3.10/site-packages'


class Temp:
    root = f'{_PROJ_DIR}/temp'
    fake_oss_storage = f'{root}/.fake_oss_storage'
    unittests = f'{root}/.unittests'


apps = Apps()
conf = Conf()
oss = Oss()
project = Project()
pypi = PyPI()
python = Python()
temp = Temp()
