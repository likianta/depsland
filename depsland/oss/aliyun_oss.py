import atexit
import typing as t
from functools import partial
from os.path import basename

from lk_utils import fs

from ._base import BaseOss
from ._base import BaseOssPath
from .. import paths

if __name__ == '__main__':
    # TODO: we are going to remove `oss2` dependency, use `requests` or -
    #   `urllib` instead.
    from oss2 import Auth
    from oss2 import Bucket


class AliyunOss(BaseOss):
    type = 'aliyun'
    path: 'AliyunOssPath'
    _auto: 'Auth'
    _bucket: 'Bucket'
    _pypi: t.Set[str]
    _pypi_has_changed: bool
    
    def __init__(
        self,
        appid: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        endpoint: str,
        **_
    ) -> None:
        from oss2 import Auth, Bucket
        self.path = AliyunOssPath(appid)
        self._auth = Auth(access_key, secret_key)
        self._bucket = Bucket(self._auth, endpoint, bucket_name)
        if fs.exists(self.path.local_manifest):
            self._pypi = fs.load(self.path.local_manifest)
        else:
            self._pypi = set()
        self._pypi_has_changed = False
        
        @atexit.register
        def _save_local_manifest() -> None:
            if self._pypi_has_changed:
                print('save updated pypi manifest', len(self._pypi))
                fs.dump(self._pypi, self.path.local_manifest)
    
    @property
    def bucket(self) -> 'Bucket':
        return self._bucket
    
    def make_link(self, key: str, expires: int = 3600) -> str:
        """ make link for sharing. """
        return self._bucket.sign_url('GET', key, expires)
    
    def upload(self, file: str, link: str) -> None:
        name = basename(file)
        if x := link.startswith(self.path.pypi + '/'):
            if name in self._pypi:
                return
        self._bucket.put_object_from_file(
            link, file, progress_callback=partial(
                self._update_progress, f'uploading {name}'
            )
        )
        if x:
            self._pypi.add(name)
            self._pypi_has_changed = True
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
        if link.startswith(self.path.pypi + '/'):
            if name in self._pypi:
                self._bucket.delete_object(link)
                self._pypi.remove(name)
                self._pypi_has_changed = True
            else:
                return
        else:
            self._bucket.delete_object(link)
        print(':rpt2', f'[dim]delete done [cyan]({name})[/][/]')
    
    def pypi_sync(self) -> None:  # not used for now
        self.upload(
            self.path.local_manifest,
            '{}/manifest.pkl'.format(self.path.pypi)
        )


class AliyunOssPath(BaseOssPath):
    def __init__(self, appid: str) -> None:
        super().__init__(appid)
        self.root = f'apps/{appid}'
    
    @property
    def pypi(self) -> str:
        return 'pypi'
    
    @property
    def local_manifest(self) -> str:
        return paths.oss.pypi
