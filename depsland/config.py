import typing as t

from lk_utils import loads

from . import paths

__all__ = ['app_settings', 'controls']


class T:
    # noinspection PyTypedDict
    AppSettings = t.TypedDict('AppSettings', {
        'oss' : t.TypedDict('Oss', {
            'server': t.Literal['aliyun', 'local', 'fake'],
            'config': t.Union[
                t.TypedDict('AliyunOssConfig', {
                    'user_role'    : str,
                    'access_key'   : str,
                    'access_secret': str,
                    'endpoint'     : str,
                    'bucket_name'  : str,
                }),
                t.TypedDict('LocalOssConfig', {
                    'symlinks': bool,
                }),
                t.TypedDict('FakeOssConfig', {
                    'symlinks': bool,
                }),
            ]
        }),
        'pip' : t.TypedDict('Pip', {
            'index_url': str,
            'quiet'    : bool,
        }),
        'pypi': t.TypedDict('PyPI', {
            'update_interval': int,
        }),
    })


class GlobalControls:  # TODO: no usage yet.
    debug_mode = False
    ignore_old_manifest = False


app_settings: T.AppSettings = loads(paths.conf.depsland)
controls = GlobalControls()
