from typing import *

TKey = str
#   note: this is all lower case
#   e.g. 'numpy', 'pandas', 'lk-logger', 'pillow', etc.
TNormalizedKey = str
#   it amounts to `TKey.replace('-', '_')`
TName = str
#   note: this is case sensitive
#   e.g. 'numpy', 'pandas', 'lk_logger', 'PIL', etc.

TPath = str  # use only '/' as separator
TBaseName = str  # basename of TPath


class TPackagesInfo(TypedDict):
    name: TName
    deps: list[TNormalizedKey]
    path: tuple[TBaseName, TBaseName]
    isfile: bool


TPackges = Dict[TNormalizedKey, TPackagesInfo]
''' see `finder.py:PackageFinder:list_all_packages:returns`
    {
        str_key: {
            'name': str,
            'deps': [key, ...],
            'path': (str, str),
            'isfile': bool,
        }, ...
    }
    e.g. {
        'pillow': {
            'name': 'PIL',
            'deps': [],
            'path': (
                'C:/Program Files/Python39/Lib/site-packages/PIL',
                'C:/Program Files/Python39/Lib/site-packages/Pillow-8.2.0
                .dist-info',
            ),
            'isfile': False
        }
    }
'''
