"""
References:
    ~/venv_home/readme.md
"""
import os
from os import mkdir
from os.path import dirname
from os.path import exists
from platform import system

from lk_utils import dumps
from lk_utils import loads
from lk_utils.filesniff import normpath

from .typehint import *

# noinspection PyTypeChecker
platform = system().lower()  # type: TPlatform

curr_dir = normpath(dirname(__file__))  # current dir
pakg_dir = curr_dir  # depsland package dir
proj_dir = dirname(pakg_dir)  # depsland project dir

conf_dir = f'{proj_dir}/conf'
home_dir = f'{proj_dir}/venv_home'  # project venv_home dir
pypi_dir = f'{proj_dir}/pypi'  # project pypi dir


class _PathModel:
    pyversion: TPyVersion
    platform: TPlatform
    
    def __str__(self):
        raise NotImplementedError
    
    def indexing_dirs(self, pyversion):
        self.pyversion = pyversion
    
    def build_dirs(self):
        raise NotImplementedError


class VEnvSourceModel(_PathModel):
    inventory: str
    venvlinks: str
    
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
    
    def __init__(self, pyversion: TPyVersion, platform=platform):
        self.pyversion = pyversion
        self.platform = platform
        
        self.inventory = f'{home_dir}/inventory'
        self.venvlinks = f'{home_dir}/venv_links'
        
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
        assert exists(self.venvlinks)
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
        return f'{self.python}/{self.pyversion}._pth'
    
    @property
    def pip_suits(self) -> List[str]:
        return os.listdir(assets_model.pip) + \
               os.listdir(assets_model.setuptools)
    
    @property
    def tk_suits(self) -> List[str]:
        return os.listdir(assets_model.tkinter)


class VEnvDistModel(_PathModel):
    home: str
    dlls: str
    lib: str
    scripts: str
    site_packages: str
    
    def __init__(self, name):
        self.home = f'{home_dir}/venv_links/{name}'
        
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
            #   them by `.main._init_venv_dir:MARK@20210915105256`
            
            mkdir(self.lib)
            mkdir(self.site_packages)
    
    @property
    def python_exe(self):
        return f'{self.home}/python.exe'
    
    @property
    def python_pth(self):
        return f'{self.home}/{self.pyversion}._pth'


class EmbedAssetsModel(_PathModel):
    """ ~/build/assets/* """
    embed_python: str
    pip: str
    pip_src: str
    setuptools: str
    tkinter: str
    urllib3: str
    
    def __init__(self, pyversion):
        self.pyversion = pyversion
        self.indexing_dirs(pyversion)
    
    def __str__(self):
        raise NotImplemented
    
    def indexing_dirs(self, pyversion):
        super().indexing_dirs(pyversion)
        
        from embed_python_manager import PyVersion
        from embed_python_manager.path_model import AssetsPathModel
        
        model = AssetsPathModel(PyVersion(self.pyversion))
        
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
    
    def load_indexed_data(self) -> Tuple[
        TNameVersions, TDependenciesIndex, TUpdates
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
            self, a: TNameVersions, b: TDependenciesIndex, c: TUpdates
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
assets_model = EmbedAssetsModel('python39')
pypi_model = LocalPyPIModel()
src_model = VEnvSourceModel('python39', platform)

__all__ = [
    'platform',
    'curr_dir', 'pakg_dir', 'proj_dir',
    'conf_dir', 'home_dir', 'pypi_dir',
    'VEnvSourceModel', 'VEnvDistModel', 'EmbedAssetsModel', 'LocalPyPIModel',
    'assets_model', 'pypi_model', 'src_model',
]
