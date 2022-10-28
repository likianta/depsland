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


class _PathIndex:  # DELETE
    root: str
    
    def __init__(self):
        self._build_dirs()
    
    def _build_dirs(self):
        pass


class Project(_PathIndex):
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

class Apps(_PathIndex):
    root = f'{_PROJ_DIR}/apps'
    venv = f'{root}/.venv'
    _packages = f'{root}/.venv/{{appid}}/packages'
    
    def make_packages(self, appid: str, clear_exists=False) -> str:
        packages = self._packages.format(appid=appid)
        if exists(packages):
            if clear_exists:
                fs.remove_tree(packages)
                os.mkdir(packages)
        else:
            os.makedirs(packages)
        return packages


class Conf(_PathIndex):
    root = f'{_PROJ_DIR}/conf'
    oss_client = f'{root}/oss_client.yaml'
    oss_server = f'{root}/oss_server.yaml'
    pip = f'{root}/pip.yaml'


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


class Python(_PathIndex):
    root = f'{_PROJ_DIR}/python'
    if _IS_WINDOWS:
        raise NotImplementedError
    else:
        pip = f'{root}/bin/pip'
        python = f'{root}/bin/python3.10'
        site_packages = f'{root}/lib/python3.10/site-packages'


class Temp(_PathIndex):
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

# -----------------------------------------------------------------------------

''' DELETE
class _PathModel:
    pyversion: T.PyVersion
    platform: T.Platform
    
    def __str__(self):
        raise NotImplementedError
    
    def indexing_dirs(self, pyversion):
        self.pyversion = pyversion
    
    def build_dirs(self):
        raise NotImplementedError


class VEnvSourceModel(_PathModel):
    inventory: str
    instances: str
    
    venv_home: str
    plat_home: str
    pypi_home: str
    
    cache: str
    downloads: str
    
    python: str
    dlls: str
    lib: str
    scripts: str
    site_packages: str
    
    def __init__(self, pyversion: T.PyVersion, platform=platform):
        self.pyversion = pyversion
        self.platform = platform
        
        self.inventory = f'{home_dir}/inventory'
        self.instances = f'{home_dir}/instances'
        
        self.venv_home = home_dir
        self.plat_home = f'{home_dir}/inventory/{platform}'
        self.pypi_home = pypi_dir
        
        self.cache = f'{self.pypi_home}/cache'
        self.downloads = f'{self.pypi_home}/downloads'
        
        self.indexing_dirs(pyversion)
    
    def __str__(self):
        if not hasattr(self, 'python'):
            raise NotImplemented(
                'You need to call `SourcePathManager.indexing_dirs` to update '
                '`self.python`'
            )
        return self.python
    
    def indexing_dirs(self, pyversion):
        super().indexing_dirs(pyversion)
        
        self.python = f'{self.plat_home}/{pyversion}'
        
        self.dlls = f'{self.python}/dlls'
        self.lib = f'{self.python}/lib'
        self.scripts = f'{self.python}/scripts'
        
        self.site_packages = f'{self.lib}/site-packages'
    
    def build_dirs(self):
        assert exists(self.venv_home)
        assert exists(self.inventory)
        assert exists(self.instances)
        assert exists(self.plat_home)
        
        # if not exists(self.plat_home):
        #     mkdir(self.plat_home)
        
        # do not create these dirs, the external manager will do.
        # see `.main._init_venv_dir:MARK@20210915153053` and `.setup.setup
        # ._setup_embed_python`
        # if not exists(self.python):
        #     mkdir(self.python)
        #
        #     mkdir(self.dlls)
        #     mkdir(self.lib)
        #     mkdir(self.scripts)
        #
        #     mkdir(self.site_packages)
    
    @property
    def python_exe(self):
        return os.path.normpath(f'{self.python}/python.exe')
    
    @property
    def python_pth(self):
        return f'{self.python}/{self.pyversion.full_name}._pth'
    
    @property
    def pip_suits(self) -> t.List[str]:
        return os.listdir(assets_model.pip) + \
               os.listdir(assets_model.setuptools)
    
    @property
    def tk_suits(self) -> t.List[str]:
        return os.listdir(assets_model.tkinter)


class VEnvDistModel(_PathModel):
    """
    folder structure:
        depsland/venv_home/instances
            |= home                     # `(attr) home`
                |= dlls                 # `(attr) dlls`
                |= lib                  # `(attr) lib`
                    |= site-packages    # `(attr) site_packages`
                |= scripts              # `(attr) scripts`
    """
    home: str
    dlls: str
    lib: str
    scripts: str
    site_packages: str
    
    def __init__(self, name):
        self.home = f'{home_dir}/instances/{name}'
        
        self.dlls = f'{self.home}/dlls'
        self.lib = f'{self.home}/lib'
        self.scripts = f'{self.home}/scripts'
        
        self.site_packages = f'{self.lib}/site-packages'
        
        # self.build_dirs()
    
    def __str__(self):
        return self.home
    
    def build_dirs(self):
        if not exists(self.home):
            mkdir(self.home)
            
            # # mkdir(self.dlls)
            # # mkdir(self.scripts)
            #   do not create 'dlls' and 'scripts' dirs, we will make links to
            #   them by `./main.py : (def) _init_venv_dir`.
            
            mkdir(self.lib)
            mkdir(self.site_packages)
    
    @property
    def python_exe(self):
        return f'{self.home}/python.exe'
    
    @property
    def python_pth(self):
        # e.g. '{self.home}/python38._pth'
        return f'{self.home}/{self.pyversion.full_name}._pth'


class EmbedAssetsModel(_PathModel):
    """ ~/build/assets/* """
    embed_python: str
    pip: str
    pip_src: str
    setuptools: str
    tkinter: str
    urllib3: str
    
    def __init__(self, pyversion: T.PyVersion):
        self.pyversion = pyversion
        self.indexing_dirs(pyversion)
    
    def __str__(self):
        raise NotImplemented
    
    def indexing_dirs(self, pyversion):
        super().indexing_dirs(pyversion)
        
        from embed_python_manager.path_model import AssetsPathModel
        # FIXME(risk): `embed_python_manager.pyversion.PyVersion` is outdated
        #   and unmatched with depsland's one.
        model = AssetsPathModel(self.pyversion)
        
        self.embed_python = model.embed_python
        self.pip = model.pip_in_pip_suits
        self.pip_src = model.pip_src_in_pip_suits
        self.setuptools = model.setuptools_in_pip_suits
        self.urllib3 = model.urllib3_in_pip_suits
        
        # FIXME: we need to check tkinter 32/64 bit version.
        if model.pyversion.major == 2:
            self.tkinter = model.tk_suits_py2
        else:
            self.tkinter = model.tk_suits_py3
    
    def build_dirs(self):
        pass


class LocalPyPIModel(_PathModel):
    """ ~/pypi/* """
    home: str
    
    cache: str
    downloads: str
    extraced: str
    index: str
    
    name_version: str
    # locations: str
    dependencies: str
    updates: str
    
    def __init__(self):
        self.indexing_dirs(pypi_dir)
    
    def __str__(self):
        return self.home
    
    def indexing_dirs(self, home):
        self.home = home
        
        self.cache = f'{self.home}/cache'
        self.downloads = f'{self.home}/downloads'
        self.extraced = f'{self.home}/extracted'
        self.index = f'{self.home}/index'
        
        self.name_version = f'{self.index}/name_version.pkl'
        # self.locations = f'{self.index}/locations.pkl'  # DELETE
        self.dependencies = f'{self.index}/dependencies.pkl'
        self.updates = f'{self.index}/updates_record.pkl'
    
    def build_dirs(self):
        assert exists(self.home)
        for d in (
                self.cache,
                self.downloads,
                self.extraced,
                self.index,
        ):
            if not exists(d):
                mkdir(d)
    
    def mkdir(self, name_id):
        d = f'{self.extraced}/{name_id}'
        if not exists(d):
            os.mkdir(d)
        elif not os.listdir(d):
            pass
        else:
            raise FileExistsError
        return d
    
    def load_indexed_data(self) -> t.Tuple[
        T.NameVersions, T.DependenciesIndex, T.Updates
    ]:
        """
        See `depsland/repository.py`
        """
        bundle = self.get_indexed_files()
        if all(map(exists, bundle)):
            # noinspection PyTypeChecker
            return tuple(map(loads, bundle))
        else:
            from collections import defaultdict
            return (
                defaultdict(list),
                defaultdict(list),
                dict()
            )
    
    def save_indexed_data(
            self, a: T.NameVersions, b: T.DependenciesIndex, c: T.Updates
    ):
        for data, file in zip((a, b, c), self.get_indexed_files()):
            dumps(data, file)
    
    def get_indexed_files(self):
        return (
            self.name_version,
            # self.locations,
            self.dependencies,
            self.updates,
        )


# noinspection PyTypeChecker
# assets_model = EmbedAssetsModel(PyVersion('3.9'))
# pypi_model = LocalPyPIModel()
# src_model = VEnvSourceModel(PyVersion('3.9'), platform)
'''
