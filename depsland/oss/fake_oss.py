from lk_utils import fs

from .local_oss import LocalOss
from .local_oss import LocalOssPath
from .. import paths


class FakeOss(LocalOss):
    type = 'fake'
    
    # noinspection PyMissingConstructor
    def __init__(self, appid: str, symlinks: bool = False, **_):
        self.path = FakeOssPath(appid)
        self._symlinks = symlinks


class FakeOssPath(LocalOssPath):
    # noinspection PyMissingConstructor
    def __init__(self, appid: str):
        self.appid = appid
        self.root = f'{paths.oss.test}/{appid}'
        fs.make_dir(f'{self.root}')
        fs.make_dir(f'{self.root}/assets')
        fs.make_dir(f'{self.root}/pypi')
