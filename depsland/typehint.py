from typing import *

if __name__ == '__main__':
    from depsland.pip import Pip as _Pip
    from depsland.data_struct import PackageInfo as _PackageInfo
    from depsland.data_struct import Requirement as _Requirement
    from depsland.paths import EmbedAssetsModel as _Struct1
    from depsland.paths import VEnvSourceModel as _Struct2
    from depsland.paths import VEnvDistModel as _Struct3
else:
    _PackageInfo = None
    _Pip = None
    _Requirement = None
    _Struct1 = None
    _Struct2 = None
    _Struct3 = None

TPackageInfo = _PackageInfo
TPathStruct = Union[_Struct1, _Struct2, _Struct3]
TPip = _Pip
TRequirement = _Requirement

# -----------------------------------------------------------------------------

TVersionSpec = str
#   followed PEP-440 canonical form (with clause symbols like '>=', '!=' etc).
#   additionally supported special keywords: see `.data_struct.special_versions`
TVersion = str
#   followed PEP-440 canonical form (without clause symbols).
#   additionally supported special keywords: see `.data_struct.special_versions`
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
TPyVersionNum = Literal[
    '2.7', '2.7-32',
    '3.0', '3.0-32',
    '3.1', '3.1-32',
    '3.2', '3.2-32',
    '3.3', '3.3-32',
    '3.4', '3.4-32',
    '3.5', '3.5-32',
    '3.6', '3.6-32',
    '3.7', '3.7-32',
    '3.8', '3.8-32',
    '3.9', '3.9-32',
]

TPlatform = Literal[
    'linux', 'macos', 'windows'
]

TRawName = str
TName = str
#   e.g. 'numpy', 'pandas', 'lk-logger', 'pillow', etc.
TNameId = str  # f'{TName}-{TFixedVersion}'

TPath = str  # use only '/' as separator
TBaseName = str  # basename of TPath

# `repository.py > class:LocalPyPI`
TNameVersions = Dict[TName, List[TVersion]]
TLocation = TPath
TDependencies = List[TNameId]
TDependenciesIndex = Dict[TNameId, TDependencies]
TUpdates = Dict[TName, int]
