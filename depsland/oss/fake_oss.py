from os.path import exists

from lk_utils import fs

from .oss import Oss
from .. import paths


class FakeOss(Oss):
    
    # noinspection PyMissingConstructor
    def __init__(self, appid: str, **_):
        self._path = FakeOssPath(appid)
        self._root = paths.temp.fake_oss_storage
    
    def upload(self, file: str, link: str) -> None:
        dst_name = fs.filename(link)
        assert dst_name.endswith(('.zip', '.fzip', '.pkl')), link
        fs.copy_file(file, f'{self._root}/{dst_name}')
        print(':rpt', f'[magenta](fake_oss) upload done '
                      f'[cyan]({fs.basename(file)})[/][/]')
    
    def download(self, link: str, file: str) -> None:
        src_name = fs.filename(link)
        assert src_name.endswith(('.zip', '.fzip', '.pkl')), link
        fs.copy_file(f'{self._root}/{src_name}', file)
        print(':rpt', f'[magenta](fake_oss) download done '
                      f'[cyan]({fs.basename(file)})[/][/]')


class FakeOssPath:
    
    def __init__(self, appid: str):
        self.appid = appid
        self._root = f'{paths.temp.fake_oss_storage}/{appid}'
        if not exists(self._root):
            fs.make_dir(self._root)
    
    def __str__(self):
        return f'<fake:/temp/.fake_oss_storage/{self.appid}>'
    
    @property
    def manifest(self) -> str:
        return f'{self._root}/manifest.pkl'
    
    @property
    def assets(self) -> str:
        return f'{self._root}/assets'
    
    @property
    def pypi(self) -> str:
        return f'{self._root}/pypi'
