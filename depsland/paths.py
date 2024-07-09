"""
ref: ~/docs/project-structure.md
"""
import os
import sys
from os.path import exists

from lk_utils import fs

__all__ = [
    'apps',
    'build',
    'config',
    'oss',
    'project',
    'pypi',
    'python',
    'system',
    'temp',
]


class _Env:
    CONFIG_ROOT = os.getenv('DEPSLAND_CONFIG_ROOT')
    PYPI_ROOT = os.getenv('DEPSLAND_PYPI_ROOT')
    PYTHON_STANDALONE = os.getenv('DEPSLAND_PYTHON_STANDALONE', '1')


class System:
    def __init__(self) -> None:
        self.is_windows = os.name == 'nt'
        if self.is_windows:
            self.depsland = os.getenv('DEPSLAND')  # note this may be None
            self.desktop = fs.normpath(os.environ['USERPROFILE'] + '/Desktop')
            self.home = fs.normpath(os.environ['USERPROFILE'])
            self.local_app_data = fs.normpath(os.environ['LOCALAPPDATA'])
            self.start_menu = fs.normpath(
                os.environ['APPDATA'] + '/Microsoft/Windows/Start Menu/Programs'
            )
            self.temp = fs.normpath(os.environ['TEMP'])
        else:
            pass  # TODO


class Project:
    def __init__(self) -> None:
        if exists(x := fs.xpath('../.depsland_project.json')):
            project_info: dict = fs.load(x)
            self.project_mode = project_info['project_mode']
        else:
            project_info: dict = {}
            self.project_mode = ''
        
        # project_mode
        #   '': it means depsland is installed by pip.
        #   'development': it means project is cloned by git.
        #   'production': it means this is a standalone version. see also -
        #       `build/build.py : full_build`
        
        if self.project_mode == '':
            self.root = fs.xpath('.project', True)
            if not exists(self.root):
                print(
                    'first time run depsland, init a virtual project root...',
                    ':v2',
                )
                self._init_project_root(self.root)
        
        elif self.project_mode == 'development':
            self.root = fs.xpath('..', force_abspath=True)
        
        elif self.project_mode == 'production':
            self.root = fs.xpath('..', force_abspath=True)
            
            dir0 = fs.xpath('../..')
            dir1 = fs.xpath('../../current')
            assert fs.dirname(dir0) == 'depsland'  # TEST
            assert (curr_ver := project_info['depsland_version'])
            #   this key is set by `build/build.py:full_build`
            
            if exists(dir1):
                # fmt:off
                if (
                    fs.load('{}/.depsland_project.json'.format(dir1))
                    .get('depsland_version') != curr_ver
                ):
                    fs.remove(dir1)
                # fmt:on
            if not exists(dir1):
                '''
                create following directories/files:
                    <user-programs>
                        |- depsland
                            |- 0.8.0
                                |- depsland
                                    |- paths.py     # <- we are here
                                    |- ...
                                |- .depsland_project.json
                                |- Depsland.exe
                                |- Depsland (Debug).exe
                                |- ...
                            |- current              # 1. symlink to 0.8.0
                            |- Depsland.lnk         # 2. 0.8.0/Depsland.exe
                            |- Depsland (Debug).lnk
                                # 3. 0.8.0/Depsland (Debug).exe
                    <desktop>
                        |- Depsland.lnk
                                # 4. <user-programs>/current/Depsland.exe
                '''
                print(
                    'first time run depsland, init production environment...',
                    ':v2'
                )
                fs.make_link(fs.xpath('..'), dir1)
                fs.make_shortcut(
                    f'{dir1}/Depsland.exe',
                    f'{dir0}/Depsland.lnk',
                    True
                )
                fs.make_shortcut(
                    f'{dir1}/Depsland (Debug).exe',
                    f'{dir0}/Depsland (Debug).lnk',
                    True
                )
                fs.make_shortcut(
                    f'{dir1}/Depsland.exe',
                    '<desktop>/Depsland.lnk',
                    True
                )
        
        elif self.project_mode == 'shipboard':
            self.root = fs.xpath('..', force_abspath=True)
            fs.make_shortcut(
                '{}/Depsland.exe'.format(self.root),
                '<desktop>/Depsland.lnk',
                None
            )
        
        else:
            raise Exception(self.project_mode)
        
        # ---------------------------------------------------------------------
        
        self.apps = f'{self.root}/apps'
        self.build = f'{self.root}/build'
        self.config = f'{self.root}/config'
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
    def _init_project_root(root: str) -> None:
        """
        see: `build/build.py:backup_project_resources`
        """
        os.mkdir(f'{root}')
        os.mkdir(f'{root}/apps')
        os.mkdir(f'{root}/apps/.bin')
        os.mkdir(f'{root}/apps/.venv')
        # os.mkdir(f'{root}/build')  # later
        # os.mkdir(f'{root}/config')  # later
        os.mkdir(f'{root}/dist')
        os.mkdir(f'{root}/oss')
        os.mkdir(f'{root}/oss/apps')
        os.mkdir(f'{root}/oss/test')
        os.mkdir(f'{root}/pypi')
        os.mkdir(f'{root}/pypi/cache')
        os.mkdir(f'{root}/pypi/downloads')
        os.mkdir(f'{root}/pypi/index')
        os.mkdir(f'{root}/pypi/index/snapdep')
        os.mkdir(f'{root}/pypi/installed')
        # os.mkdir(f'{root}/python')  # later
        # os.mkdir(f'{root}/sidework')  # later
        os.mkdir(f'{root}/temp')
        os.mkdir(f'{root}/temp/.self_upgrade')
        os.mkdir(f'{root}/temp/.unittests')
        # os.mkdir(f'{root}/unittests')
        
        # make link
        fs.make_link(sys.base_exec_prefix, f'{root}/python')
        
        # unzip files
        from .utils.ziptool import extract_file
        
        extract_file(fs.xpath('chore/build.zip'), f'{root}/build')
        extract_file(fs.xpath('chore/config.zip'), f'{root}/config')
        extract_file(fs.xpath('chore/sidework.zip'), f'{root}/sidework')
        
        # init files
        fs.dump({}, f'{root}/pypi/index/id_2_paths.json')
        fs.dump({}, f'{root}/pypi/index/name_2_vers.json')


# -----------------------------------------------------------------------------


class Apps:
    def __init__(self) -> None:
        self.root = f'{project.root}/apps'
        self.bin = f'{self.root}/.bin'
        self.venv = f'{self.root}/.venv'
        self._distribution_history = f'{self.root}/{{appid}}/.dist_history'
        self._installation_history = f'{self.root}/{{appid}}/.inst_history'
        self._venv_packages = f'{self.root}/.venv/{{appid}}/{{version}}'
        ''' the difference between `_distribution_history` and
            `_installation_history`:
            when developer builds or publishes a new version of an app, the
            dist history will be updated, the inst doesn't.
            when user installs a new version of an app, the vice versa.
            this avoids that if a developer plays himself as role of an user,
            published and installed the same app on the same machine, the
            incremental-update scheme reported "target version exists" error.
        '''
    
    def get_distribution_history(self, appid: str) -> str:
        return self._distribution_history.format(appid=appid)
    
    def get_installation_history(self, appid: str) -> str:
        return self._installation_history.format(appid=appid)
    
    def get_packages(self, appid: str, version: str) -> str:
        return self._venv_packages.format(appid=appid, version=version)
    
    def make_packages(
        self, appid: str, version: str, clear_exists: bool = False
    ) -> str:
        """
        create or clear a folder for venv packages.
        """
        packages = self._venv_packages.format(appid=appid, version=version)
        if exists(d := fs.dirpath(packages)):
            if exists(packages):
                if clear_exists:
                    fs.remove_tree(packages)
                    os.mkdir(packages)
            else:
                os.mkdir(packages)
        else:
            os.mkdir(d)
            os.mkdir(packages)
        return packages


class Build:
    def __init__(self) -> None:
        self.root = f'{project.root}/build'
        self.icon = f'{self.root}/icon'  # the folder
        if sys.platform == 'darwin':
            self.launcher_icon = f'{self.root}/icon/launcher.icns'
        elif sys.platform == 'linux':
            self.launcher_icon = f'{self.root}/icon/launcher.png'
        elif sys.platform == 'win32':
            self.launcher_icon = f'{self.root}/icon/launcher.ico'
        else:
            raise Exception(sys.platform)


class Config:
    """
    redirect config:
        there are two ways to redirect config root:
            1. the dynamic way:
                by setting environment variable `DEPSLAND_CONFIG_ROOT`
            2. the static way:
                put a file '.redirect' in `config` folder. the file content is \
                a relative or absolute path points to the new config root.
        the dynamic is prior to the static.
    """
    
    def __init__(self) -> None:
        if x := _Env.CONFIG_ROOT:
            self.root = fs.abspath(x)
            print(':r', f'[yellow dim]relocate config root to {self.root}[/]')
        elif exists(f'{project.root}/config/.redirect'):
            with open(f'{project.root}/config/.redirect', 'r') as f:
                x = f.read().strip()
                if os.path.isabs(x):
                    self.root = fs.normpath(x)
                else:  # e.g. '../tests/config'
                    self.root = fs.normpath(f'{project.root}/config/{x}')
            print(':r', f'[yellow dim]relocate config root to {self.root}[/]')
        else:
            self.root = f'{project.root}/config'
        
        self.auto_saved = f'{self.root}/auto_saved.pkl'
        self.depsland = f'{self.root}/depsland.yaml'
        # self.oss_client = f'{self.root}/oss_client.yaml'
        # self.oss_server = f'{self.root}/oss_server.yaml'


class Oss:  # note: this is a local dir that mimics OSS structure.
    def __init__(self) -> None:
        self.root = f'{project.root}/oss'
        self.apps = f'{self.root}/apps'
        self.test = f'{self.root}/test'
        self.pypi = f'{self.root}/pypi.pkl'


class PyPI:
    """
    to redirect pypi root, use environment variable 'DEPSLAND_PYPI_ROOT'.
    see also: `build/init.py`
    """
    
    def __init__(self) -> None:
        if x := _Env.PYPI_ROOT:
            print(':r', f'[yellow dim]relocate pypi root to "{x}"[/]')
            self.root = fs.abspath(x)
        else:
            self.root = f'{project.root}/pypi'
        self.is_symlink = fs.islink(self.root)
        self.real_root = (
            fs.normpath(os.path.realpath(self.root))
            if self.is_symlink else self.root
        )
        
        # DELETE: is it better not to use custom cache dir?
        self.cache = f'{self.root}/cache'
        self.downloads = f'{self.root}/downloads'
        self.index = f'{self.root}/index'
        self.installed = f'{self.root}/installed'
        
        self.id_2_paths = f'{self.index}/id_2_paths.json'
        self.name_2_vers = f'{self.index}/name_2_vers.json'
        self.snapdep = f'{self.index}/snapdep'


class Python:
    def __init__(self) -> None:
        if project.project_mode and _Env.PYTHON_STANDALONE == '1':
            self.root = f'{project.root}/python'
            assert len(os.listdir(self.root)) > 3, (
                'cannot find standalone python interpreter. \n'
                'if you want to setup one, please follow the instruction of '
                '`{}/python/README.zh.md`; \n'
                'if you do not want to setup, you can set the environment '
                'variable `DEPSLAND_PYTHON_STANDALONE` to "0"'.format(
                    project.root
                )
            )
        else:
            self.root = fs.normpath(sys.base_exec_prefix)
        if system.is_windows:
            self.pip = f'{self.root}/Scripts/pip.exe'
            self.python = f'{self.root}/python.exe'
            self.site_packages = f'{self.root}/Lib/site-packages'
        else:
            self.pip = f'{self.root}/bin/pip'
            self.python = f'{self.root}/bin/python3'
            if self.root.startswith(f'{project.root}/python'):
                self.site_packages = f'{self.root}/lib/python3.11/site-packages'
            else:
                self.site_packages = '{}/lib/python{}.{}/site-packages'.format(
                    self.root, *sys.version_info[:2]
                )


class Temp:
    def __init__(self) -> None:
        self.root = f'{project.root}/temp'
        self.self_upgrade = f'{self.root}/.self_upgrade'
        self.unittests = f'{self.root}/.unittests'


system = System()
project = Project()

apps = Apps()
build = Build()
config = Config()
oss = Oss()
pypi = PyPI()
python = Python()
temp = Temp()
