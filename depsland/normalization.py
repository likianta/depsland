import re
import typing as t
from dataclasses import dataclass


class T:
    RawName = str  # e.g. 'lk-logger', 'PySide6', etc.
    RawVersionSpec = str  # e.g. '>=5.4.6a0'
    
    Name = str  # e.g. 'lk_logger', 'pyside6', etc.
    Version = str  # a semantic version.
    #   it could be empty, means 'any version'.
    #   there is no such thing like: '0.0.0', 'latest', 'any', '*', because \
    #   they are not semantic versions.
    VersionSpec = t.ForwardRef('VersionSpec')


@dataclass
class VersionSpec:
    # https://pip.pypa.io/en/stable/cli/pip_install/#requirement-specifiers
    name: T.Name  # e.g. 'lk_logger'
    version: T.Version
    comparator: str  # '>=', '>', '==', '<', '<=', '!=', '~=', ''
    
    # def __init__(self, name: T.Name, version: T.Version, comparator: str):
    #     if version == '0.0.0':
    #         assert comparator in ('>=', '==', '')
    #         version = ''
    #         comparator = ''
    #     self.name = name
    #     self.version = version
    #     self.comparator = comparator
    
    def __str__(self):
        return self.full_spec
    
    def __repr__(self):
        return f'VersionSpec[{self.full_spec}]'
    
    @property
    def spec(self) -> str:  # e.g. '>=5.4.6a0'
        return f'{self.comparator}{self.version}'
    
    @property
    def full_spec(self) -> str:  # e.g. 'lk_logger>=5.4.6a0'
        return f'{self.name}{self.comparator}{self.version}'


def check_name_normalized(name: str) -> bool:
    return name == normalize_name(name)


def normalize_anyname(raw: str) -> t.Tuple[T.Name, t.Tuple[T.VersionSpec, ...]]:
    """
    examples:
        'PySide6' -> ('pyside6', ())
        'PySide6 >=6.0.4, <6.1' -> (
            'pyside6',
            (<spec of '>=6.0.4'>, <spec of '<6.1.0'>)
        )
    """
    a, b = re.search(r'([^ <>=!~]+)(.*)', raw.replace(' ', '')).groups()
    name = normalize_name(a)
    if b:
        return name, tuple(normalize_verspecs(name, b))
    else:
        # return name, (VersionSpec(name, '', ''),)
        return name, ()


def normalize_name(raw_name: T.RawName) -> T.Name:
    """
    examples:
        'PySide6'           -> 'pyside6'
        'PyYAML'            -> 'pyyaml'
        'lk-logger'         -> 'lk_logger'
        'jaraco.classes'    -> 'jaraco_classes'
            https://pypi.tuna.tsinghua.edu.cn/simple/jaraco-classes/
    """
    return raw_name.lower().replace('-', '_').replace('.', '_')


# def normalize_name_and_verspecs(raw_name: str) -> t.Tuple[
#     T.Name, t.Iterator[T.VersionSpec]
# ]:
#     """
#     examples:
#         'PySide6 >=6.0.4, <6.1' -> (
#             'pyside6',
#             (<spec of '>=6.0.4'>, <spec of '<6.1.0'>)
#         )
#     """
#     a, b = re.search(r'([^ <>=!~]+)(.+)', raw_name.replace(' ', '')).groups()
#     name = normalize_name(a)
#     verspecs = normalize_verspecs(name, b)
#     return name, verspecs


def normalize_verspecs(
    name: T.Name, raw_verspec: T.RawVersionSpec
) -> t.Iterator[T.VersionSpec]:
    """
    e.g.
        '4.5.3'         ->  <spec of '==4.5.3'>
        '>=4.5.0'       ->  <spec of '>=4.5.0'>
        '>=4.5,<5.0'    ->  <spec of '>=4.5.0,<5.0.0'>
        '==4.*'         ->  <spec of '>=4.0,<5.0'>
        '==4.3.*'       ->  <spec of '>=4.3.0,<4.4.0'>
        'latest'        ->  <spec of ''>
        'any'           ->  <spec of ''>
        '*'             ->  <spec of ''>
    """
    if not raw_verspec:
        yield VersionSpec(name, '', '')
        return
    
    from .verspec import semver_parse
    
    pattern_to_split_comp_and_ver = re.compile(r'([<>=!~]*)(.+)')
    
    for part in raw_verspec.split(','):
        comp, ver = pattern_to_split_comp_and_ver.search(part).groups()
        if comp == '':
            comp = '=='
        
        if ver in ('latest', 'any', '*'):
            assert comp == '=='
            yield VersionSpec(
                name=name,
                version='',
                comparator='',
            )
        
        elif '*' not in ver:
            yield VersionSpec(
                name=name,
                version=ver,
                comparator=comp,
            )
        
        else:
            assert comp in ('>=', '==')
            assert (
                m := re.search(r'((?:\d\.)+)\*$', ver)
            ), 'the asterisk symbol could only be in minor or patch position'
            minor_or_patch = 'minor' if m.group(1).count('.') == 1 else 'patch'
            bottom_ver = semver_parse(ver)
            bumped_ver = (
                bottom_ver.bump_major()
                if minor_or_patch == 'minor'
                else bottom_ver.bump_minor()
            )
            yield VersionSpec(
                name=name, version=str(bottom_ver), comparator='>='
            )
            yield VersionSpec(
                name=name, version=str(bumped_ver), comparator='<'
            )


def split_dirname_of_dist_info(dirname: str) -> t.Tuple[T.Name, T.Version]:
    # e.g. 'qmlease-3.1.0a15.dist-info' -> ('qmlease', '3.1.0a15')
    dirname = dirname.replace('.dist-info', '')
    name, version = dirname.split('-')
    name = normalize_name(name)
    return name, version


def split_filename_of_package(filename: str) -> t.Tuple[T.Name, T.Version]:
    """
    examples:
        'PyYAML-6.0-cp310-cp310-macosx_10_9_x86_64.whl' -> ('pyyaml', '6.0')
        'lk-logger-4.0.7.tar.gz' -> ('lk_logger', '4.0.7')
        'aliyun-python-sdk-2.2.0.zip' -> ('aliyun_python_sdk', '2.2.0')
    """
    for ext in ('.whl', '.tar.gz', '.zip'):
        if filename.endswith(ext):
            barename = filename[:-len(ext)]
            break
    else:
        raise ValueError(filename)
    # assert ext
    if ext == '.whl':
        a, b, _ = barename.split('-', 2)
    else:
        a, b = barename.rsplit('-', 1)
    a = normalize_name(a)
    return a, b
