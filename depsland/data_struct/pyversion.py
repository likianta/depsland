import re


class T:
    from typing import Literal
    
    VersionRaw = Literal[
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
    Version = Literal[
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
    VersionNoDot = Literal[
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
    VersionFullName = Literal[
        # 'python27',
        # 'python30',
        # 'python31',
        # 'python32',
        # 'python33',
        # 'python34',
        # 'python35',
        'python36',
        'python37',
        'python38',
        'python39',
        'python310',
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
        # return: e.g. '3.8', '3.9', '3.10', ...
        return self._version
    
    @property
    def full_name(self) -> T.VersionFullName:
        # return: e.g. 'python38'
        return 'python' + self.no_dot  # noqa
    
    @property
    def v(self) -> T.Version:  # the same as `__str__`
        # return: e.g. '3.8', '3.9', '3.10', ...
        return self._version
    
    @property
    def no_dot(self) -> T.VersionNoDot:
        # return: e.g. '38', '39', '310', ...
        return f'{self.major}{self.minor}'  # noqa
        #   this is equivalent to `self._version.replace('.', '')`
    
    @property
    def is_64bit(self) -> bool:
        return self._width == 64
