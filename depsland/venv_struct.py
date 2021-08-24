"""
References:
    ~/venv_home/readme.md
"""
from os import mkdir
from os.path import dirname, exists
from platform import system

from lk_utils.filesniff import normpath

from .typehint import TPlatform, TPyVersion

platform = system().lower()
curr_dir = normpath(dirname(__file__))  # current dir
pakg_dir = curr_dir  # depsland package dir
proj_dir = dirname(pakg_dir)  # depsland project dir
home_dir = f'{proj_dir}/venv_home'  # project venv_home dir
pypi_dir = f'{proj_dir}/pypi'  # project pypi dir


class SourcePathManager:
    
    def __init__(self, pyversion: TPyVersion, platform: TPlatform):
        self.pyversion = pyversion
        self.platform = platform
        
        self.inventory = f'{home_dir}/inventory'
        self.venvlinks = f'{home_dir}/venv_links'
        
        self.venv_home = home_dir
        self.plat_home = f'{home_dir}/inventory/{platform}'
        self.pypi_home = pypi_dir
        
        self.cache = f'{self.pypi_home}/cache'
        self.downloads = f'{self.pypi_home}/downloads'
        
        self.pip_suits = None  # list[path]
        self.tk_suits = None  # list[path]
        
        self.indexing_dirs(pyversion)
    
    def __str__(self):
        if not hasattr(self, 'python'):
            raise NotImplemented(
                'You need to call `SourcePathManager.indexing_dirs` to update '
                '`self.python`'
            )
        return self.python
    
    # noinspection PyAttributeOutsideInit
    def indexing_dirs(self, pyversion):
        self.pyversion = pyversion
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
            
            # from .setup import download_embed_python
            # download_embed_python(self.pyversion, self.platform)
            
            from .setup import get_pip, get_tkinter
            self.pip_suits = get_pip(self.pyversion, dst_dir=self.site_packages)
            self.tk_suits = get_tkinter(self.pyversion, dst_dir=self.python)


class DestinationPathManager:
    
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
            
            mkdir(self.dlls)
            mkdir(self.lib)
            mkdir(self.scripts)
            
            mkdir(self.site_packages)
    
    @property
    def interpreter(self):
        return f'{self.home}/python.exe'


# noinspection PyTypeChecker
path_mgr = SourcePathManager('python39', platform)

__all__ = [
    'platform', 'curr_dir', 'pakg_dir', 'proj_dir', 'home_dir', 'pypi_dir',
    'SourcePathManager', 'DestinationPathManager', 'path_mgr',
]
