import re
from distutils.version import LooseVersion
from distutils.version import StrictVersion

from dephell_specifier import RangeSpecifier
from lk_logger import lk


class T:
    import typing as t
    List = t.List
    Optional = t.Optional
    Union = t.Union
    
    VersionRaw = t.Literal[
        # '2.7', '2.7-32',
        # '3.0', '3.0-32',
        # '3.1', '3.1-32',
        # '3.2', '3.2-32',
        # '3.3', '3.3-32',
        # '3.4', '3.4-32',
        # '3.5', '3.5-32',
        '3.6', '3.6-32',
        '3.7', '3.7-32',
        '3.8', '3.8-32',
        '3.9', '3.9-32',
        '3.10', '3.10-32',
    ]
    Version = t.Literal[
        # '2.7',
        # '3.0',
        # '3.1',
        # '3.2',
        # '3.3',
        # '3.4',
        # '3.5',
        '3.6',
        '3.7',
        '3.8',
        '3.9',
        '3.10',
    ]
    VersionNoDot = t.Literal[
        # '27',
        # '30',
        # '31',
        # '32',
        # '33',
        # '34',
        # '35',
        '36',
        '37',
        '38',
        '39',
        '310',
    ]
    VersionSpec = str
    #   followed PEP-440 canonical form (with clause symbols like '>=', '!='
    #   etc). additionally supported special keywords: see `.data_struct
    #   .special_versions`
    
    NameId = str  # e.g. 'numpy-1.13.3'
    
    Platform = t.Literal[
        'linux', 'macos', 'windows'
    ]


class PyVersion:
    major: int
    minor: int
    _version: T.Version
    _width: int  # 32 or 64
    
    def __init__(self, version: T.VersionRaw):
        assert (m := re.match(r'^([23])\.(\d+)(?:-32)?$', version)), \
            ('Illegal version pattern!', version)
        self.major = int(m.group(1))  # 2 or 3
        self.minor = int(m.group(2))  # 6, 7, 8, ...
        self._version = version.replace('-32', '')  # noqa
        self._width = 32 if version.endswith('-32') else 64
    
    def __str__(self) -> T.Version:
        return self._version
    
    @property
    def v(self) -> T.Version:  # the same as `__str__`
        return self._version
    
    @property
    def no_dot(self) -> T.VersionNoDot:
        # return: e.g. '38', '39', '310', ...
        return f'{self.major}{self.minor}'  # noqa
        #   this is equivalent to `self._version.replace('.', '')`
    
    @property
    def is_64bit(self) -> bool:
        return self._width == 64


IGNORE = 'ignore'
LATEST = '*'


def find_best_matched_version(
        ver_spec: T.VersionSpec, ver_list: T.List[T.Version]
) -> T.Optional[T.Version]:
    """

    args:
        ver_spec: 'version specifier', e.g. '>=3.0', '==1.*', '>=1.2,!=1.2.4',
            ...
        ver_list: a group of fixed version numbers.
            e.g. ['2014.04', '2.0.0.post3', '1.0.2a0', '1.0.2', ...]
            note the elements have already been sorted by descending order.
            i.e. `ver_list[0]` is latest version, `ver_list[-1]` is oldest.
            see PEP-440: https://www.python.org/dev/peps/pep-0440/#version
            -specifiers

    references:
        https://github.com/dephell/dephell_specifier
            usages:
                from dephell_specifier import RangeSpecifier
                print('3.4' in RangeSpecifier('*'))  # -> True
                print('3.4' in RangeSpecifier('<=2.7'))  # -> False
                print('3.4' in RangeSpecifier('>2.7'))  # -> True
    """
    # case 1
    if not ver_list:
        return None
    
    # case 2
    if ver_list == [IGNORE]:  # see `pypi.py > LocalPyPI > _refresh_local
        #   _repo > code:'lk.logt('[D3411]', 'ignoring this req', req) ...'`
        return IGNORE
    else:
        assert IGNORE not in ver_list
    
    # case 3
    if ver_spec in (LATEST, ''):
        return ver_list[0]
    
    # case 4
    spec = RangeSpecifier(ver_spec)
    for v in ver_list:
        if v in spec:
            return v
    else:
        return None


def sort_versions(versions: T.List[T.Version], reverse=True):
    """
    References:
        Sort versions in Python:
            https://stackoverflow.com/questions/12255554/sort-versions-in-python
            /12255578
        The LooseVersion and StrictVersion difference:
            https://www.python.org/dev/peps/pep-0386/
    """
    
    def _normalize_version(v: T.Union[T.NameId, T.Version]):
        # TODO: the incoming `param:v` type must be TVersion; TNameId should be
        #   removed.
        if '-' in v:
            v = v.split('-', 1)[-1]
        if v in ('', '*', 'latest'):
            return '999999.999.999'
        else:
            return v
    
    try:
        versions.sort(key=lambda v: StrictVersion(_normalize_version(v)),
                      # `x` type is Union[TNameId, TVersion], for TNameId we
                      # need to split out the name part.
                      reverse=reverse)
    except ValueError as exception_point:
        lk.logt('[I1543]', f'strict version comparison failed because of: '
                           f'"{exception_point}"', 'use loose compare instead')
        try:
            versions.sort(key=lambda v: LooseVersion(_normalize_version(v)),
                          reverse=reverse)
        except Exception as e:
            lk.logt('[E2123]', versions)
            raise e
    return versions
