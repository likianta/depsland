from lk_utils import fs

from ._base import BaseOss
from ._base import BaseOssPath
from .. import paths


class LocalOss(BaseOss):
    
    def __init__(self, appid: str, **_):
        self.path = LocalOssPath(appid)
    
    def upload(self, file: str, link: str) -> None:
        # the link is a local path from `self.path`.
        name = fs.filename(file)
        fs.copy_file(file, link, True)
        print(':trp', f'upload done [cyan]({name})[/]')
    
    def download(self, link: str, file: str) -> None:
        name = fs.filename(file)
        fs.copy_file(link, file, True)
        print(':trp', f'download done [cyan]({name})[/]')
    
    def delete(self, link: str) -> None:
        name = fs.filename(link)
        fs.remove_file(link)
        print(':trp', f'[dim]delete done [cyan]({name})[/][/]')


class LocalOssPath(BaseOssPath):
    def __init__(self, appid: str):
        super().__init__(appid)
        self._root = f'{paths.oss.apps}/{appid}'
        fs.make_dir(self._root)
