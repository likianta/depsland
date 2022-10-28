import typing as t
from lk_utils import loads
from .fake_oss import FakeOss
from .oss import Oss
from .. import config
from ..paths import conf as conf_paths


def get_oss_server() -> t.Union[Oss, FakeOss]:
    if config.debug_mode:
        return FakeOss()
    else:
        return Oss(**_load_config(conf_paths.oss_server))  # noqa


def get_oss_client() -> t.Union[Oss, FakeOss]:
    if config.debug_mode:
        return FakeOss()
    else:
        return Oss(**_load_config(conf_paths.oss_client))  # noqa


def _load_config(file: str) -> dict:
    out = loads(file)
    assert all(out.values()), 'the oss config is not prepared!'
    return out


class OssPath:
    
    def __init__(self, appid: str):
        self.appid = appid
    
    def __str__(self):
        return f'<bucket:/depsland/apps/{self.appid}>'
    
    @property
    def manifest(self) -> str:
        return f'apps/{self.appid}/manifest.pkl'
    
    @property
    def assets(self) -> str:
        return f'apps/{self.appid}/assets'
