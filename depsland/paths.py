"""
ref: ~/docs/project-structure.md
"""
import os
import sys
from collections import defaultdict
from os.path import exists

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

__all__ = [
    'apps',
    'build',
    'conf',
    'oss',
    'project',
    'pypi',
    'python',
    'system',
    'temp',
]


class System:
    
    def __init__(self):
        self.is_windows = os.name == 'nt'
        if self.is_windows:
            self.depsland = os.getenv('DEPSLAND')  # note it may be None
            self.desktop = fs.normpath(os.environ['USERPROFILE'] + '/Desktop')
            self.home = fs.normpath(os.environ['USERPROFILE'])
            self.local_app_data = fs.normpath(os.environ['LOCALAPPDATA'])
            self.start_menu = fs.normpath(
                os.environ['APPDATA']
                + '/Microsoft/Windows/Start Menu/Programs'
            )
            self.temp = fs.normpath(os.environ['TEMP'])
        else:
            pass  # TODO


class Project:
    
    def __init__(self):
        if exists(fs.xpath('../.depsland_project')):
            self.root = fs.xpath('..', force_abspath=True)
            self.is_project_mode = True
        else:
            self.root = fs.xpath('.project', True)
            self.is_project_mode = False
            if not exists(self.root):
                print(':v2', 'first time run depsland, init a virtual '
                             'project root...')
                self._init_project_root(self.root)
        
        self.apps = f'{self.root}/apps'
        self.build = f'{self.root}/build'
        self.conf = f'{self.root}/conf'
        self.depsland = f'{self.root}/depsland'
        self.dist = f'{self.root}/dist'
        self.manifest_json = f'{self.root}/manifest.json'
        self.manifest_pkl = f'{self.root}/manifest.pkl'
        self.oss = f'{self.root}/oss'
        self.project = f'{self.root}'
        self.pypi = f'{self.root}/pypi'
        self.python = f'{self.root}/python'
        self.temp = f'{self.root}/temp'
    
    @staticmethod
    def _init_project_root(root: str):
        """
        related: build/backup_project_resources.py
        """
        os.mkdir(f'{root}')
        os.mkdir(f'{root}/apps')
        os.mkdir(f'{root}/apps/.bin')
        os.mkdir(f'{root}/apps/.venv')
        # os.mkdir(f'{root}/build')  # later
        # os.mkdir(f'{root}/conf')  # later
        os.mkdir(f'{root}/dist')
        os.mkdir(f'{root}/oss')
        os.mkdir(f'{root}/oss/apps')
        os.mkdir(f'{root}/oss/test')
        os.mkdir(f'{root}/pypi')
        os.mkdir(f'{root}/pypi/cache')
        os.mkdir(f'{root}/pypi/downloads')
        os.mkdir(f'{root}/pypi/index')
        os.mkdir(f'{root}/pypi/installed')
        # os.mkdir(f'{root}/python')  # later
        # os.mkdir(f'{root}/sidework')  # later
        os.mkdir(f'{root}/temp')
        os.mkdir(f'{root}/temp/.self_upgrade')
        os.mkdir(f'{root}/temp/.unittests')
        os.mkdir(f'{root}/unittests')
        
        # make link
        fs.make_link(sys.base_exec_prefix, f'{root}/python')
        
        # unzip files
        from .utils.ziptool import decompress_file
        decompress_file(fs.xpath('chore/build.zip'), f'{root}/build')
        decompress_file(fs.xpath('chore/conf.zip'), f'{root}/conf')
        decompress_file(fs.xpath('chore/sidework.zip'), f'{root}/sidework')
        
        # init files
        dumps(defaultdict(list), f'{root}/pypi/index/dependencies.pkl')
        dumps(defaultdict(list), f'{root}/pypi/index/name_2_versions.pkl')
        dumps({}, f'{root}/pypi/index/name_id_2_paths.pkl')
        dumps({}, f'{root}/pypi/index/updates.pkl')


# -----------------------------------------------------------------------------

class Apps:
    
    def __init__(self):
        self.root = f'{project.root}/apps'
        self.bin = f'{self.root}/.bin'
        self.venv = f'{self.root}/.venv'
        self._distribution_history = f'{self.root}/{{appid}}/.dist_history'
        self._installation_history = f'{self.root}/{{appid}}/.inst_history'
        self._packages = f'{self.root}/.venv/{{appid}}'
        ''' the difference between `_distribution_history` and
            `_installation_history`:
            when developer builds or publishes a new version of an app, the
            dist history will be updated, the inst won't.
            when user installs a new version of an app, the vice versa.
            this avoids that if a developer as also an user, published and
            installed the same app on the same machine, the incremental-update
            scheme reported "target version exists" error.
        '''
    
    def get_distribution_history(self, appid: str) -> str:
        return self._distribution_history.format(appid=appid)
    
    def get_installation_history(self, appid: str) -> str:
        return self._installation_history.format(appid=appid)
    
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


class Build:
    
    def __init__(self):
        self.root = f'{project.root}/build'
        self.launcher_ico = f'{self.root}/exe/launcher.ico'


class Conf:
    
    def __init__(self):
        self.root = f'{project.root}/conf'
        self.depsland = f'{self.root}/depsland.yaml'
        self.oss_client = f'{self.root}/oss_client.yaml'
        self.oss_server = f'{self.root}/oss_server.yaml'
        
        if exists(x := f'{project.conf}/.redirect'):
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
    
    def __init__(self):
        self.root = f'{project.root}/oss'
        self.apps = f'{self.root}/apps'
        self.test = f'{self.root}/test'


class PyPI:
    
    def __init__(self):
        self.root = f'{project.root}/pypi'
        
        self.cache = f'{self.root}/cache'
        self.downloads = f'{self.root}/downloads'
        self.index = f'{self.root}/index'
        self.installed = f'{self.root}/installed'
        
        self.dependencies = f'{self.root}/index/dependencies.pkl'
        self.name_2_versions = f'{self.root}/index/name_2_versions.pkl'
        self.name_id_2_paths = f'{self.root}/index/name_id_2_paths.pkl'
        self.updates = f'{self.root}/index/updates.pkl'
        
        assert exists(self.dependencies)
        assert exists(self.name_2_versions)
        assert exists(self.name_id_2_paths)
        assert exists(self.updates)


class Python:
    
    def __init__(self):
        if project.is_project_mode:
            self.root = f'{project.root}/python'
        else:
            self.root = sys.base_exec_prefix
        if system.is_windows:
            self.pip = f'{self.root}/Scripts/pip.exe'
            self.python = f'{self.root}/python.exe'
            self.site_packages = f'{self.root}/Lib/site-packages'
        else:
            self.pip = f'{self.root}/bin/pip'
            self.python = f'{self.root}/bin/python3.10'
            self.site_packages = f'{self.root}/lib/python3.10/site-packages'


class Temp:
    
    def __init__(self):
        self.root = f'{project.root}/temp'
        self.self_upgrade = f'{self.root}/.self_upgrade'
        self.unittests = f'{self.root}/.unittests'


system = System()
project = Project()

apps = Apps()
build = Build()
conf = Conf()
oss = Oss()
pypi = PyPI()
python = Python()
temp = Temp()
