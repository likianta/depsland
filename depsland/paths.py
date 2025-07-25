"""
ref: ~/docs/project-structure.md
"""
import os
import sys
import typing as t
from os.path import exists

from lk_utils import fs
from lk_utils import new_thread

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
    
    @staticmethod
    @new_thread()
    def set_environment_variables(depsland_dir: str) -> None:
        """
        issue: `winreg` can create env var successfully, but when we open a new
        process and check the env we had just set, it shows none unless reboot.
            ref: https://stackoverflow.com/questions/71253807
            resolved: https://stackoverflow.com/a/63840426/9695911
        """
        # quick check
        depsland_dir = fs.abspath(depsland_dir).replace('/', '\\')
        if os.getenv('DEPSLAND') == depsland_dir:
            return
        
        # --- a) use `setx`
        # FIXME: `setx` command runs very slow in some computer.
        # from lk_utils import run_cmd_args
        # depsland_dir = fs.abspath(depsland_dir).replace('/', '\\')
        # run_cmd_args('setx', 'DEPSLAND', depsland_dir, verbose=True)
        # run_cmd_args('setx', 'PYTHONUTF8', '1', verbose=True)
        
        # --- b) use winreg
        import ctypes
        import winreg
        
        class EnvironmentVariablesAccess:
            
            def __init__(self) -> None:
                self._registry = self._open_registry()
            
            @staticmethod
            def _open_registry() -> winreg.HKEYType:
                """
                ref: https://stackoverflow.com/questions/573817
                """
                return winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER, 'Environment', 0,
                    winreg.KEY_ALL_ACCESS
                )
            
            def get_key(self, key: str) -> str:
                try:
                    value, _ = winreg.QueryValueEx(self._registry, key)
                    return value
                except Exception:  # ValueError or FileNotFoundError
                    return ''
            
            def set_key(self, key: str, val: str) -> None:
                winreg.SetValueEx(
                    self._registry, key, 0, winreg.REG_EXPAND_SZ, val
                )
            
            # noinspection PyPep8Naming
            def close(self) -> None:
                winreg.CloseKey(self._registry)
                # tell other processes to update their environment
                # https://stackoverflow.com/a/63840426/9695911
                HWND_BROADCAST = 0xFFFF
                WM_SETTING_CHANGED = 0x1A
                SMTO_ABORT_IF_HUNG = 0x0002
                ctypes.windll.user32.SendMessageTimeoutW(
                    HWND_BROADCAST, WM_SETTING_CHANGED, 0, 'Environment',
                    SMTO_ABORT_IF_HUNG, 1000, ctypes.byref(ctypes.c_long())
                )
        
        env = EnvironmentVariablesAccess()
        env.set_key('DEPSLAND', depsland_dir)
        env.close()


class Project:
    def __init__(self) -> None:
        root, mode = self._init_project()
        self.root = root
        self.project_mode = mode
        
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
    
    def _init_project(self) -> t.Tuple[str, str]:
        project_file = fs.xpath('../.depsland_project.json')
        if exists(project_file):
            project_info: dict = fs.load(project_file)
        else:
            project_info: dict = {'project_mode': 'package'}
        
        """
        project_info: {
            'project_mode': (
                'development' | 'package' | 'production' | 'shipboard'
            ),
            #   'development': it means project is cloned by git.
            #   'package': it means depsland is installed by pip.
            #   'production': it means this is a standalone version. see also
            #       `build/build.py : full_build`
            #   'shipboard': ...
            'depsland_version': str,
            'initialized': `<app_path>-<created_time>-<bool>`,
            #   see doc in /wiki/docs/devnote/how-do-we-check-paths-initialized
            #   .md
        }
        """
        
        def check_initialized() -> bool:
            if project_mode == 'development':
                return True
            elif project_mode == 'package':
                return exists(project_root)
            else:
                if project_info.get('initialized'):
                    v0: str = project_info['initialized']
                    if v0.endswith('false'):
                        return False
                    else:
                        v1 = '{}-{}-{}'.format(
                            project_root, fs.filetime(project_file, 'c'), 'true'
                        )
                        return v1 == v0
                else:
                    return False
        
        project_mode = project_info['project_mode']
        project_root = (
            fs.xpath('.project') if project_mode == 'package' else
            fs.xpath('..')
        )
        initialized = check_initialized()
        
        if initialized:
            return project_root, project_mode
        
        # ---------------------------------------------------------------------
        
        if project_mode == 'development':
            self._setup_development_mode()
        elif project_mode == 'package':
            self._setup_package_mode(project_root)
        elif project_mode == 'production':
            self._setup_production_mode(project_root, project_info)
        elif project_mode == 'shipboard':
            self._setup_shipboard_mode(project_root)
        else:
            raise ValueError(f'unknown project mode: {project_mode}')
        
        project_info['initialized'] = '{}-{}-{}'.format(
            project_root, fs.filetime(project_file, 'c'), 'true'
        )
        fs.dump(project_info, project_file)
        
        return project_root, project_mode
    
    @staticmethod
    def _setup_development_mode() -> None:
        os.environ['LK_LOGGER_FORCE_COLOR'] = '1'
        
    @staticmethod
    def _setup_package_mode(root: str) -> None:
        print('first time run depsland, init a virtual project root...', ':v1')
        
        # see: `build/build.py:backup_project_resources`
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
        
    def _setup_production_mode(
        self, project_root: str, project_info: dict
    ) -> None:
        self._fix_blocked_dlls()
        
        def build_tree_1(dir0: str, dir1: str) -> None:
            """
            tree like:
                <user-programs>
                    |- depsland                 # dir0
                        |- 0.8.0                # project_root
                            |- depsland
                                |- paths.py     # <- we are here
                                |- ...
                            |- .depsland_project.json
                            |- ...
                        |- current              # dir1 (may not exist)
            create following directories/files:
                <user-programs>
                    |- depsland                 # dir0
                        |- 0.8.0                # project_root
                            |- depsland
                                |- paths.py     # <- we are here
                                |- ...
                            |- .depsland_project.json
                            |- Depsland.exe
                            |- Depsland (Debug).exe
                            |- ...
                        |- current              # dir1 (to be created)
                            # 1. symlink to '0.8.0'
                        |- Depsland.lnk
                            # 2. '0.8.0/Depsland.exe'
                        |- Depsland (Debug).lnk
                            # 3. '0.8.0/Depsland (Debug).exe'
                <desktop>
                    |- Depsland.lnk
                            # 4. '<user-programs>/current/Depsland.exe'
            """
            fs.make_link(project_root, dir1)
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
        
        def build_tree_2() -> None:
            """
            tree like:
                <user-programs>
                    |- depsland             # project_root
                        |- depsland
                            |- paths.py     # <- we are here
                            |- ...
                        |- .depsland_project.json
                        |- ...
            
            just create desktop shortcut:
                <user-programs>
                    |- depsland             # project_root
                        |- depsland
                            |- paths.py     # <- we are here
                            |- ...
                        |- .depsland_project.json
                        |- Depsland.exe
                        |- Depsland (Debug).exe
                        |- ...
                <desktop>
                    |- Depsland.lnk
                        # 1. '<user-programs>/depsland/Depsland.exe'
            """
            fs.make_shortcut(
                f'{project_root}/Depsland.exe',
                '<desktop>/Depsland.lnk',
                True
            )
        
        # there are two types of folder structure, we use different ways to
        # init them.
        if fs.dirname(fs.parent(project_root)).lower() == 'depsland':
            '''
            <user-programs>
                |- depsland                 # dir0
                    |- 0.8.0                # project_root
                        |- depsland
                            |- paths.py     # <- we are here
                            |- ...
                        |- .depsland_project.json
                        |- ...
                    |- current              # dir1 (may not exist)
            '''
            dir0 = fs.xpath('../..')
            dir1 = fs.xpath('../../current')
            if exists(dir1):
                if (
                    # fmt:off
                    fs.load('{}/.depsland_project.json'.format(dir1))
                    .get('depsland_version') == project_info['depsland_version']
                    #   this key is set by `build/build.py:full_build`
                    # fmt:on
                ):
                    # note: this should not happen...
                    # -- A
                    # raise Exception(dir1, curr_ver)
                    # -- B
                    # system.set_environment_variables(dir1)
                    # return
                    # -- C
                    print(':v6', 'target tree alraedy built!', dir1)
                else:
                    fs.remove(dir1)
            if not exists(dir1):
                print(
                    'first time run depsland, init production environment...',
                    ':v1'
                )
                build_tree_1(dir0, dir1)
            self._setup_system_environment(dir1)
        
        else:
            build_tree_2()
            self._setup_system_environment(project_root)
    
    def _setup_shipboard_mode(self, project_root: str) -> None:
        self._fix_blocked_dlls()
        '''
        <user_programs>
            |- <depsland_bundled_app>
                |- source               # project_root
                    |- depsland
                        |- paths.py     # <- we are here
                        |- ...
                    |- .depsland_project.json
                    |- ...
                |- <App Name>.exe
                |- <App Name> (Debug).exe
        '''
        fs.make_shortcut(
            '{}/Depsland.exe'.format(project_root),
            '<desktop>/Depsland.lnk',
            None
        )
        self._setup_system_environment(project_root)
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _fix_blocked_dlls() -> None:
        # note: windows only
        print('fix blocked dlls before opening GUI on winforms.', ':pv1')
        
        def unblock_dlls(dir: str) -> None:
            """
            related: `depsland.api.dev_api.offline_build._init_dist_tree`
            ref:
                https://stackoverflow.com/questions/20886450/unblock-a-file-in
                -windows-from-a-python-script
                https://stackoverflow.com/questions/76214672/failed-to
                -initialize-python-runtime-dll
            """
            for f in fs.findall_files(dir, '.dll'):
                zid = os.path.abspath(f.path) + ':Zone.Identifier'
                if os.path.isfile(zid):  # check if blocked
                    print(':v5', 'unblock', f.relpath)
                    try:
                        os.remove(zid)  # unblock then
                    except WindowsError:
                        # FIXME: some computers may raise [WinError 2] the -
                        #   system cannot find the file specified.
                        pass
        
        site_packages_dir = fs.xpath('../chore/site_packages')
        unblock_dlls('{}/pythonnet'.format(site_packages_dir))
        unblock_dlls('{}/toga_winforms'.format(site_packages_dir))
    
    @staticmethod
    def _setup_system_environment(dir: str) -> None:
        system.set_environment_variables(dir)


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
        
        self.exe = f'{self.root}/exe'  # the folder
        # self.icon = f'{self.root}/icon'  # the folder
        
        self.depsland_runapp_exe = \
            f'{self.exe}/depsland-runapp.exe'
        self.depsland_runapp_console_exe = \
            f'{self.exe}/depsland-runapp-console.exe'
        self.depsland_runapp_debug_exe = \
            f'{self.exe}/depsland-runapp-debug.exe'
        
        ext = {'darwin': 'icns', 'linux': 'png', 'win32': 'ico'}[sys.platform]
        self.help_icon = '{}/icon/help.{}'.format(self.root, ext)
        self.launcher_icon = '{}/icon/launcher.{}'.format(self.root, ext)
        self.python_icon = '{}/icon/python.{}'.format(self.root, ext)


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
            print(':v1', f'relocate config root to {self.root}')
        elif exists(f'{project.root}/config/.redirect'):
            with open(f'{project.root}/config/.redirect', 'r') as f:
                x = f.read().strip()
                if os.path.isabs(x):
                    self.root = fs.normpath(x)
                else:  # e.g. '../tests/config'
                    self.root = fs.normpath(f'{project.root}/config/{x}')
            print(':v1', f'relocate config root to {self.root}')
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
            print(':v1', f'relocate pypi root to "{x}"')
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
        if project.project_mode != 'package' and _Env.PYTHON_STANDALONE == '1':
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
