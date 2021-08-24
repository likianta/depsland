"""
Download embedded python executables.
"""
import os

from lk_logger import lk

from ..typehint import *
from ..utils import unzip_file
from ..manager.venv_manager import path_mgr, platform


def download_embed_python(pyversion: TPyVersion, platform=platform):
    manager = EmbedPythonManager(pyversion, platform)
    manager.download(extract=True)
    manager.test()
    
    # disable _pth file
    if os.path.exists(f := f'{manager.bin_dir}/{pyversion}._pth'):
        os.rename(f, f + '.bak')


class EmbedPythonManager:
    
    def __init__(self, pyversion: TPyVersion, platform=platform,
                 download_dir=''):
        self.pyversion = pyversion
        self.platform = platform
        self.bin_dir = path_mgr.bin
        self.download_dir = download_dir or self.bin_dir
    
    def download(self, extract=False):
        """
        Download embed python file (.zip) to `path_mgr.curr_home`, then unzip
        file to `path_mgr.bin`
        """
        link = get_download_link(self.pyversion, self.platform)
        file = path_mgr.curr_home + '/' + link.rsplit("/")[-1]
        
        from ..downloader import download
        download(link, file, exist_ok=True)
        
        if extract:
            dst_dir = unzip_file(file, path_mgr.bin)
            lk.loga('see unzipped result', dst_dir)
        # else you can extract it manually later.
        
        return file
    
    def test(self):
        from lk_utils import send_cmd
        lk.loga(send_cmd(f'{self.interpreter} -V'))
    
    @property
    def interpreter(self):
        return f'{self.bin_dir}/python.exe'


def get_download_link(pyversion, platform=platform):
    urls = {
        'windows': {
            # https://www.python.org/downloads/windows/
            'python35'   : 'https://www.python.org/ftp/python/'
                           '3.5.4/python-3.5.4-embed-amd64.zip',
            'python35-32': 'https://www.python.org/ftp/python/'
                           '3.5.4/python-3.5.4-embed-win32.zip',
            'python36'   : 'https://www.python.org/ftp/python/'
                           '3.6.8/python-3.6.8-embed-amd64.zip',
            'python36-32': 'https://www.python.org/ftp/python/'
                           '3.6.8/python-3.6.8-embed-win32.zip',
            'python37'   : 'https://www.python.org/ftp/python/'
                           '3.7.9/python-3.7.9-embed-amd64.zip',
            'python37-32': 'https://www.python.org/ftp/python/'
                           '3.7.9/python-3.7.9-embed-win32.zip',
            'python38'   : 'https://www.python.org/ftp/python/'
                           '3.8.10/python-3.8.10-embed-amd64.zip',
            'python38-32': 'https://www.python.org/ftp/python/'
                           '3.8.10/python-3.8.10-embed-win32.zip',
            'python39'   : 'https://www.python.org/ftp/python/'
                           '3.9.5/python-3.9.5-embed-amd64.zip',
            'python39-32': 'https://www.python.org/ftp/python/'
                           '3.9.5/python-3.9.5-embed-win32.zip',
        },
        # TODO: more platforms needed
    }
    try:
        return urls[platform][pyversion]
    except KeyError:
        raise Exception('Unexpected Python version', platform, pyversion)
