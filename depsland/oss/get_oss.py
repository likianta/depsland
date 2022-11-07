import typing as t

from lk_utils import loads

from .fake_oss import FakeOss
from .oss import Oss
from .. import config
from ..paths import conf as conf_paths


def get_oss_server(appid: str) -> t.Union[Oss, FakeOss]:
    if config.debug_mode:
        return FakeOss(appid=appid)
    else:
        return Oss(appid=appid, **_load_config(conf_paths.oss_server))


def get_oss_client(appid: str) -> t.Union[Oss, FakeOss]:
    if config.debug_mode:
        return FakeOss(appid=appid)
    else:
        return Oss(appid=appid, **_load_config(conf_paths.oss_client))


def _load_config(file: str) -> dict:
    out = loads(file)
    assert all(out.values()), 'the oss config is not prepared!'
    return out
