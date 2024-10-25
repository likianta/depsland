import typing as t

from conflore import Conflore
from lk_utils import load

from . import paths

__all__ = ['app_settings', 'auto_saved', 'controls']


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
    
    # noinspection PyTypedDict
    AutoSaved = t.Union[
        Conflore,
        t.TypedDict('AutoSaved', {
            'appstore': t.TypedDict('AppStore', {
                'last_input': str
            })
        })
    ]


class GlobalControls:  # TODO: no usage yet.
    debug_mode = False
    ignore_old_manifest = False


app_settings: T.AppSettings = load(paths.config.depsland)
controls = GlobalControls()
auto_saved: T.AutoSaved = Conflore(
    paths.config.auto_saved,
    {'appstore': {'last_input': ''}},
)
