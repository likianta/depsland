from functools import partial
from os.path import basename

from ._base import BaseOss
from ._base import BaseOssPath


class AliyunOss(BaseOss):
    type = 'aliyun'
    
    def __init__(self, appid: str,
                 access_key: str, access_secret: str,
                 endpoint: str, bucket_name: str, **_):
        # TODO: we are going to remove `oss2` dependency, instead, use \
        #   `requests`.
        #   oss2 requires pycryptodome, which causes OSError that missing \
        #   'Crypto.Cipher._raw_ecb' on windows.
        from oss2 import Auth
        from oss2 import Bucket
        self.path = AliyunOssPath(appid)
        self._auth = Auth(access_key, access_secret)
        self._bucket = Bucket(self._auth, endpoint, bucket_name)
    
    @property
    def bucket(self):
        return self._bucket
    
    def make_link(self, key: str, expires=3600) -> str:
        """ make link for sharing. """
        return self._bucket.sign_url('GET', key, expires)
    
    def upload(self, file: str, link: str) -> None:
        name = basename(file)
        # noinspection PyUnusedLocal
        resp = self._bucket.put_object_from_file(
            link, file, progress_callback=partial(
                self._update_progress, f'uploading {name}'
            )
        )
        print(':rpt2', f'upload done [cyan]({name})[/]')
    
    def download(self, link: str, file: str) -> None:
        name = basename(file)
        # noinspection PyUnusedLocal
        resp = self._bucket.get_object_to_file(
            link, file, progress_callback=partial(
                self._update_progress, f'downloading {name}'
            )
        )
        print(':rpt2', f'download done [cyan]({name})[/]')
    
    def delete(self, link: str) -> None:
        name = basename(link)
        self._bucket.delete_object(link)
        print(':rpt2', f'[dim]delete done [cyan]({name})[/][/]')


class AliyunOssPath(BaseOssPath):
    def __init__(self, appid: str):
        super().__init__(appid)
        self.root = f'apps/{appid}'
