import re
import typing as t
from dataclasses import dataclass


class T:
    RawName = str  # e.g. 'lk-logger', 'PySide6', etc.
    RawVersionSpec = str  # e.g. '>=5.4.6a0'
    
    Name = str  # e.g. 'lk_logger', 'pyside6', etc.
    Version = str  # a semantic version
    VersionSpec = t.ForwardRef('VersionSpec')


@dataclass
class VersionSpec:
    # https://pip.pypa.io/en/stable/cli/pip_install/#requirement-specifiers
    name: T.Name  # e.g. 'lk_logger'
    version: T.Version
    comparator: str  # '>=', '>', '==', '<', '<=', '!=', '~=', ''
    
    def __repr__(self):
        return f'VersionSpec[{self.full_spec}]'
    
    @property
    def spec(self) -> str:  # e.g. '>=5.4.6a0'
        return f'{self.comparator}{self.version}'
    
    @property
    def full_spec(self) -> str:  # e.g. 'lk_logger>=5.4.6a0'
        return f'{self.name}{self.comparator}{self.version}'


def split_name_and_verspec(text: str) -> t.Tuple[T.RawName, T.RawVersionSpec]:
    text = text.replace(' ', '')
    pattern = re.compile(r'([-\w]+)(.*)')
    raw_name, verspec = pattern.match(text).groups()
    return raw_name, verspec


def normalize_name(raw_name: T.RawName) -> T.Name:
    """
    e.g. 'lk-logger' -> 'lk_logger'
         'PySide6' -> 'pyside6'
    """
    return raw_name.strip().lower().replace('-', '_')


def normalize_version_spec(
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
    
    from .utils.verspec import semver_parse
    
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
            assert (m := re.search(r'((?:\d\.)+)\*$', ver)), \
                'the asterisk symbol could only be in minor or patch position'
            minor_or_patch = 'minor' if m.group(1).count('.') == 1 else 'patch'
            bottom_ver = semver_parse(ver)
            bumped_ver = (bottom_ver.bump_major() if minor_or_patch == 'minor'
                          else bottom_ver.bump_minor())
            yield VersionSpec(
                name=name,
                version=str(bottom_ver),
                comparator='>='
            )
            yield VersionSpec(
                name=name,
                version=str(bumped_ver),
                comparator='<'
            )
