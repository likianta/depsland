from typing import *

if __name__ == '__main__':
    from depsland.pip import Pip as _Pip
else:
    _Pip = None

# -----------------------------------------------------------------------------

TPip = _Pip

# TPyVersion = str
TPyVersion = Literal[
    # 'python2', 'python2-32',
    # 'python3', 'python3-32',
    'python27', 'python27-32',
    'python30', 'python30-32',
    'python31', 'python31-32',
    'python32', 'python32-32',
    'python33', 'python33-32',
    'python34', 'python34-32',
    'python35', 'python35-32',
    'python36', 'python36-32',
    'python37', 'python37-32',
    'python38', 'python38-32',
    'python39', 'python39-32',
]
TPlatform = Literal[
    'linux', 'macos', 'windows'
]

TName = str
#   e.g. 'numpy', 'pandas', 'lk-logger', 'pillow', etc.

# DELETE: `TRawName`, `TNormName`, `TRealName` are going to be removed.
TRawName = str
#   note: this is all lower case
#   e.g. 'numpy', 'pandas', 'lk-logger', 'pillow', etc.
TNormName = TName
#   it amounts to `TKey.replace('-', '_')`
TRealName = str
#   note: this is case sensitive
#   e.g. 'numpy', 'pandas', 'lk_logger', 'PIL', etc.

TPath = str  # use only '/' as separator
TBaseName = str  # basename of TPath


class TPackagesInfo(TypedDict):
    name: TRealName
    deps: list[TNormName]
    path: tuple[TBaseName, TBaseName]
    isfile: bool


TPackges = dict[TNormName, TPackagesInfo]
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
