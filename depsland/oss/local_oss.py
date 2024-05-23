import os

from lk_utils import fs

from ._base import BaseOss
from ._base import BaseOssPath
from .. import paths


class LocalOss(BaseOss):
    type = 'local'
    
    def __init__(self, appid: str, symlinks: bool = False, **_):
        self.path = LocalOssPath(appid)
        self._symlinks = symlinks  # warning: this is experimental feature.
        # self._copy = fs.make_link if symlinks else fs.copy_file
    
    def upload(self, file: str, link: str) -> None:
        # the link is a local path from `self.path`.
        name = fs.filename(file)
        if self._symlinks:
            fs.make_link(file, link, True)
        else:
            fs.copy_file(file, link, True)
        print(':t2rp', f'upload done [cyan]({name})[/]')
    
    def download(self, link: str, file: str) -> None:
        name = fs.filename(file)
        if self._symlinks:
            if os.path.realpath(link) == os.path.realpath(file):
                pass
            else:
                fs.make_link(link, file, True)
        else:
            fs.copy_file(link, file, True)
        print(':t2rp', f'download done [cyan]({name})[/]')
    
    def delete(self, link: str) -> None:
        name = fs.filename(link)
        fs.remove_file(link)
        print(':t2rp', f'[dim]delete done [cyan]({name})[/][/]')


class LocalOssPath(BaseOssPath):
    def __init__(self, appid: str):
        super().__init__(appid)
        self.root = f'{paths.oss.apps}/{appid}'
        fs.make_dir(f'{self.root}')
        fs.make_dir(f'{self.root}/assets')
        fs.make_dir(f'{self.root}/pypi')
