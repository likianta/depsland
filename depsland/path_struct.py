"""
References:
    ~/venv_home/readme.md
"""
import os
from os import mkdir
from os.path import dirname, exists
from platform import system

from lk_utils import loads
from lk_utils.filesniff import normpath

from .typehint import *

# noinspection PyTypeChecker
platform = system().lower()  # type: TPlatform
curr_dir = normpath(dirname(__file__))  # current dir
pakg_dir = curr_dir  # depsland package dir
proj_dir = dirname(pakg_dir)  # depsland project dir
home_dir = f'{proj_dir}/venv_home'  # project venv_home dir
pypi_dir = f'{proj_dir}/pypi'  # project pypi dir


class PathStruct:
    pyversion: TPyVersion
    platform: TPlatform
    
    def __str__(self):
        raise NotImplementedError
    
    def indexing_dirs(self, pyversion):
        self.pyversion = pyversion
    
    def build_dirs(self):
        raise NotImplementedError


class VEnvSourceStruct(PathStruct):
    inventory: str
    venvlinks: str
    
    venv_home: str
    plat_home: str
    pypi_home: str
    
    cache: str
    downloads: str
    
    pip_suits: list[str]
    tk_suits: list[str]
    
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
        
        if not exists(self.python):
            mkdir(self.python)
            
            mkdir(self.dlls)
            mkdir(self.lib)
            mkdir(self.scripts)
            
            mkdir(self.site_packages)
    
    @property
    def interpreter(self):
        return os.path.normpath(f'{self.python}/python.exe')
    
    @property
    def python_pth(self):
        return f'{self.python}/{self.pyversion}._pth'


class VEnvDistStruct(PathStruct):
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
        
        self.build_dirs()
    
    def __str__(self):
        return self.home
    
    def build_dirs(self):
        if not exists(self.home):
            mkdir(self.home)
            
            # mkdir(self.dlls)
            # mkdir(self.lib)
            # mkdir(self.scripts)
            
            mkdir(self.lib)
            mkdir(self.site_packages)
    
    @property
    def interpreter(self):
        return f'{self.home}/python.exe'
    
    @property
    def python_pth(self):
        return f'{self.home}/{self.pyversion}._pth'


class BuildAssetsStruct(PathStruct):
    """ ~/build/assets/* """
    assets: str
    curr_assets: str
    
    python_suits: str
    embed_python_zip: str
    pip_src: str
    pip_egg: str
    pip: str
    setuptools: str
    tkinter: str
    
    def __init__(self, pyversion, platform=platform):
        self.pyversion = pyversion
        
        self.assets = f'{proj_dir}/build/assets'
        self.curr_assets = f'{self.assets}/{platform}'
        
        self.indexing_dirs(pyversion)
    
    def __str__(self):
        return self.python_suits
    
    def indexing_dirs(self, pyversion):
        super().indexing_dirs(pyversion)
        
        if pyversion.startswith('python2'):
            self.python_suits = f'{self.curr_assets}/python2_suits'
            # TODO: self.embed_python_zip, self.pip_src, self.pip_egg
        else:
            self.python_suits = f'{self.curr_assets}/python3_suits'
            self.embed_python_zip = f'{self.python_suits}/python39_embed_win.zip'
            #   FIXME: this is related to platform
            self.pip_src = f'{self.python_suits}/pip_src/pip-21.2.4'
            self.pip_egg = f'pip-21.2.4-py3.9.egg'
        
        self.pip = f'{self.python_suits}/pip'
        self.setuptools = f'{self.python_suits}/setuptools'
        
        if pyversion.endswith('-32'):
            self.tkinter = f'{self.python_suits}/tkinter32'
        else:
            self.tkinter = f'{self.python_suits}/tkinter64'
    
    def build_dirs(self):
        raise NotImplemented


class LocalPyPIStruct(PathStruct):
    """ ~/pypi/* """
    home: str
    
    cache: str
    downloads: str
    extraced: str
    index: str
    
    name_version: str
    locations: str
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
        self.locations = f'{self.index}/locations.pkl'
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
    
    def load_indexed_data(self) -> tuple[
        TNameVersions, TLocationsIndex, TDependenciesIndex, TUpdates
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
                defaultdict(list),
                dict()
            )
    
    def get_indexed_files(self):
        return (
            self.name_version,
            self.locations,
            self.dependencies,
            self.updates,
        )


# noinspection PyTypeChecker
assets_struct = BuildAssetsStruct('python39', platform)
pypi_struct = LocalPyPIStruct()

src_struct = VEnvSourceStruct('python39', platform)
src_struct.pip_suits = os.listdir(assets_struct.pip) + \
                       os.listdir(assets_struct.setuptools)
src_struct.tk_suits = os.listdir(assets_struct.tkinter)

__all__ = [
    'platform',
    'curr_dir', 'pakg_dir', 'proj_dir', 'home_dir', 'pypi_dir',
    'PathStruct', 'VEnvSourceStruct', 'VEnvDistStruct',
    'BuildAssetsStruct', 'LocalPyPIStruct',
    'assets_struct', 'pypi_struct', 'src_struct',
]
