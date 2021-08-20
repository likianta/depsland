"""
References:
    ~/venv_home/readme.md
"""
from os import mkdir
from os.path import dirname, exists
from platform import system

from lk_utils.filesniff import normpath

from .typehint import TPyVersion, TPlatform

platform = system().lower()
curr_dir = normpath(dirname(__file__))
proj_dir = dirname(curr_dir)
home_dir = f'{proj_dir}/venv_home'


class SourcePathManager:
    
    def __init__(self, pyversion: TPyVersion, platform: TPlatform):
        self.pyversion = pyversion
        self.platform = platform

        self.inventory = f'{home_dir}/inventory'
        self.venvlinks = f'{home_dir}/venv_links'
        
        self.venv_home = home_dir
        self.plat_home = f'{home_dir}/inventory/{platform}'
        self.curr_home = None  # inited in `self.indexing_dirs`
        
        self.indexing_dirs(pyversion)

    def __str__(self):
        if not self.curr_home:
            raise NotImplemented(
                'You need to call `SourcePathManager.indexing_dirs` to update '
                '`self.curr_home`'
            )
        return self.curr_home

    # noinspection PyAttributeOutsideInit
    def indexing_dirs(self, pyversion):
        self.curr_home = f'{self.plat_home}/{pyversion}'
        
        self.bin = f'{self.curr_home}/bin'
        self.cache = f'{self.curr_home}/cache'
        self.downloads = f'{self.curr_home}/downloads'
        self.lib = f'{self.curr_home}/lib'
        self.site_packages = f'{self.curr_home}/site-packages'
        self.extra = f'{self.curr_home}/extra'
        self.scripts = f'{self.curr_home}/scripts'
        
        self.pip_suits = f'{self.extra}/package-manage-tools'
        self.tk_suits = f'{self.extra}/tkinter-tools'
        
    def build_dirs(self):
        assert exists(self.venv_home)
        assert exists(self.inventory)
        assert exists(self.venvlinks)
        
        if not exists(self.plat_home):
            mkdir(self.plat_home)
            
        if not exists(self.curr_home):
            mkdir(self.curr_home)
            
            mkdir(self.bin)
            mkdir(self.cache)
            mkdir(self.downloads)
            mkdir(self.site_packages)
            mkdir(self.extra)
            mkdir(self.scripts)
            
            mkdir(self.pip_suits)
            mkdir(self.tk_suits)
            
            # setup dirs
            # from .setup import download_embed_python
            # download_embed_python(self.pyversion, self.platform)
            
            from .setup import get_pip, get_tkinter
            get_pip(self.pyversion)
            get_tkinter(self.pyversion)


class DestinationPathManager:
    
    def __init__(self, name):
        self.home = f'{home_dir}/venv_links/{name}'
        self.dlls = f'{self.home}/dlls'
        self.lib = f'{self.home}/lib'
        self.site_packages = f'{self.home}/lib/site-packages'
        self.scripts = f'{self.home}/scripts'
        
        self.interpreter = f'{self.home}/python.exe'
        
        self.build_dirs()
    
    def __str__(self):
        return self.home
    
    def build_dirs(self):
        if not exists(self.home):
            mkdir(self.home)
            mkdir(self.dlls)
            mkdir(self.lib)
            mkdir(self.site_packages)
            mkdir(self.scripts)
            

# noinspection PyTypeChecker
path_mgr = SourcePathManager('python39', platform)
