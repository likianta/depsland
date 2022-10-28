from lk_utils import fs
from .oss import Oss
from .. import paths


class FakeOss(Oss):
    
    # noinspection PyMissingConstructor
    def __init__(self, **_):
        self._root = paths.temp.fake_oss_storage
    
    def upload(self, file: str, link: str) -> None:
        dst_name = fs.filename(link)
        assert dst_name.endswith(('.zip', '.fzip'))
        fs.copy_file(file, f'{self._root}/{dst_name}')
        print(':rpt', f'upload done [cyan]({fs.basename(file)})[/]')
    
    def download(self, link: str, file: str) -> None:
        src_name = fs.filename(link)
        assert src_name.endswith(('.zip', '.fzip'))
        fs.copy_file(f'{self._root}/{src_name}', file)
        print(':rpt', f'download done [cyan]({fs.basename(file)})[/]')
