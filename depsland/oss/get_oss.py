import typing as t

from .aliyun_oss import AliyunOss
from .fake_oss import FakeOss
from .local_oss import LocalOss
from .. import config

# ref: `..paths > Config > __init__ > the 'redirect' feature`
#      `..config > T > AppSettings > AliyunOssConfig`
oss_config = config.app_settings['oss']


class T:
    Oss = t.Union[AliyunOss, LocalOss, FakeOss]


def get_oss(appid: str, server: str = oss_config['server']) -> T.Oss:
    match server:
        case 'aliyun':
            config = oss_config['config']
            assert all(config.values()), (
                'the oss config is not filled. you may contact the author '
                '(likianta <likianta@foxmail.com>) to get the access key.'
            )
            return AliyunOss(appid=appid, **config)
        case 'local':
            return LocalOss(appid=appid)
        case 'fake':
            return FakeOss(appid=appid)
