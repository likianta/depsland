"""
ref: ~/docs/project-structure.md
"""
import os
from collections import defaultdict
from os.path import dirname
from os.path import exists

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

__all__ = [
    'apps', 'conf', 'oss', 'project', 'pypi', 'python', 'system', 'temp',
]

_CURR_DIR = fs.normpath(dirname(__file__), force_abspath=True)
_PROJ_DIR = fs.normpath(dirname(_CURR_DIR))
_IS_WINDOWS = os.name == 'nt'


class System:
    if _IS_WINDOWS:
        depsland = os.getenv('DEPSLAND')  # note it may be None
        desktop = fs.normpath(os.environ['USERPROFILE'] + '/Desktop')
        home = fs.normpath(os.environ['USERPROFILE'])
        program_data = fs.normpath(os.environ['ProgramData'])
        start_menu = fs.normpath(
            os.environ['APPDATA']
            + '/Microsoft/Windows/Start Menu/Programs'
        )
        temp = fs.normpath(os.environ['TEMP'])
    else:
        pass  # raise NotImplementedError


class Project:
    root = f'{_PROJ_DIR}'
    # below attrs follow alphabetical order
    apps = f'{root}/apps'
    apps_launcher = f'{root}/apps_launcher'
    # cache = f'{root}/cache'
    conf = f'{root}/conf'
    dist = f'{root}/dist'
    manifest_json = f'{root}/manifest.json'
    manifest_pkl = f'{root}/manifest.pkl'
    oss = f'{root}/oss'
    project = f'{root}'
    pypi = f'{root}/pypi'
    python = f'{root}/python'
    temp = f'{root}/temp'


# -----------------------------------------------------------------------------

class Apps:
    root = f'{_PROJ_DIR}/apps'
    venv = f'{root}/.venv'
    _history_versions = f'{root}/{{appid}}/.history_versions.json'
    _packages = f'{root}/.venv/{{appid}}'
    
    def get_history_versions(self, appid: str) -> str:
        return self._history_versions.format(appid=appid)
    
    def get_packages(self, appid: str) -> str:
        return self._packages.format(appid=appid)
    
    def make_packages(self, appid: str, clear_exists=False) -> str:
        packages = self._packages.format(appid=appid)
        if exists(packages):
            if clear_exists:
                fs.remove_tree(packages)
                os.mkdir(packages)
        else:
            os.mkdir(packages)
        return packages


class Conf:
    root = f'{_PROJ_DIR}/conf'
    depsland = f'{root}/depsland.yaml'
    oss_client = f'{root}/oss_client.yaml'
    oss_server = f'{root}/oss_server.yaml'
    
    def __init__(self):
        if exists(x := fs.xpath('../conf/.redirect')):
            if new_root := loads(x).strip():  # either be emptry or a dirpath.
                if not os.path.isabs(new_root):
                    # if new_root is relpath, it is relative to .redirect file.
                    new_root = fs.normpath(f'{x}/../{new_root}', True)
                assert os.path.isdir(new_root), ('invalid new_root', new_root)
                print(':r', f'[yellow dim]relocate config root: {new_root}[/]')
                self.root = new_root
                self.depsland = f'{new_root}/depsland.yaml'
                self.oss_client = f'{new_root}/oss_client.yaml'
                self.oss_server = f'{new_root}/oss_server.yaml'


class Oss:  # note: this is a local dir that mimics OSS structure.
    root = f'{_PROJ_DIR}/oss'
    apps = f'{root}/apps'
    test = f'{root}/test'


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
    self_upgrade = f'{root}/.self_upgrade'
    unittests = f'{root}/.unittests'


apps = Apps()
conf = Conf()
oss = Oss()
project = Project()
pypi = PyPI()
python = Python()
system = System()
temp = Temp()
