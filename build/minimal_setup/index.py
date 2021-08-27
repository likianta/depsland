from os import mkdir
from os.path import dirname, exists
from platform import system

platform = system().lower()

curr_dir = dirname(__file__)
proj_dir = dirname(curr_dir)
build_dir = f'{proj_dir}/build'


class ResourcesIndex:
    
    def __init__(self):
        self.assets = f'{build_dir}/assets'
        self.assets_zip = f'{build_dir}/assets.zip'
        self.requirements = f'{proj_dir}/requirements.txt'
        self.temp = f'{build_dir}/temp'
        self.venv = f'{proj_dir}/venv'
        self.venv_packages_zip = f'{build_dir}/venv_packages.zip'
        
        self.python_suits = f'{self.assets}/{platform}/python3_suits'
        self.site_packages = f'{self.venv}/lib/site-packages'
        self.venv_packages_unzip = f'{self.temp}/venv_packages'
        
        self.pip = f'{self.python_suits}/pip'
        self.pip_src = f'{self.python_suits}/pip_src'
        self.setuptools = f'{self.python_suits}/setuptools'
        self.tkinter = f'{self.python_suits}/tkinter64'
        self.python_embed = f'{self.python_suits}/python39_embed_win.zip'
        
        self._build_dirs()
    
    def _build_dirs(self):
        for i in (
                self.venv_packages_zip,
                self.venv,
                self.assets_zip,
        ):
            assert exists(i)
        
        for i in (
                self.assets,
        ):
            assert not exists(i)
        
        for i in (
                self.temp,
        ):
            if not exists(i):
                mkdir(i)
