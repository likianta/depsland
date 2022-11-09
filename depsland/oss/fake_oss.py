from lk_utils import fs

from .local_oss import LocalOss
from .local_oss import LocalOssPath
from .. import paths


class FakeOss(LocalOss):
    # noinspection PyMissingConstructor
    def __init__(self, appid: str, **_):
        self.path = FakeOssPath(appid)


class FakeOssPath(LocalOssPath):
    # noinspection PyMissingConstructor
    def __init__(self, appid: str):
        self.appid = appid
        self._root = f'{paths.oss.test}/{appid}'
        fs.make_dir(self._root)
