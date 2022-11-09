import typing as t

from lk_utils import loads

from . import paths

__all__ = ['app_settings', 'debug_mode']


class T:
    # noinspection PyTypedDict
    AppSettings = t.TypedDict('AppSettings', {
        'oss' : t.TypedDict('Oss', {
            'server': t.Literal['aliyun', 'local', 'fake'],
            'config': t.Optional[t.TypedDict('AliyunOssConfig', {
                'user_role'    : str,
                'access_key'   : str,
                'access_secret': str,
                'endpoint'     : str,
                'bucket_name'  : str,
            })]  # other servers are None.
        }),
        'pip' : t.TypedDict('Pip', {
            'index_url': str,
            'quiet'    : bool,
        }),
        'pypi': t.TypedDict('PyPI', {
            'update_interval': int,
        }),
    })


debug_mode: bool = False
app_settings: T.AppSettings = loads(paths.conf.depsland)
