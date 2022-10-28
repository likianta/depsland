import typing as t
from lk_utils import loads
from . import paths

__all__ = ['app_settings', 'debug_mode']


class T:
    # noinspection PyTypedDict
    AppSettings = t.TypedDict('AppSettings', {
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
