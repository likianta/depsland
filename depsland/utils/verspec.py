import re
import semver  # https://github.com/python-semver/python-semver
import typing as t
from ..normalization import T
from ..normalization import VersionSpec


def compare_version(v0: str, comp: str, v1: str) -> bool:
    """
    args:
        comp: '>=', '>', '==', '<', '<='
    """
    r: int = semver.compare(v0, v1)  # -1, 0, 1
    return eval(f'r {comp} 0', {'r': r})


def find_proper_version(
        request: t.Iterable[VersionSpec],
        candidates: t.Sequence[T.Version]
) -> t.Optional[str]:
    """
    args:
        request: ('1.2.3', '>=')
        candidates: a sorted list of version strings, from new to old.
    """
    if not candidates:
        return None
    
    ver_str, comp = request
    
    if comp == '':
        return candidates[0]
    if ver_str == 'latest' or ver_str == '*':
        assert comp == '=='
        return candidates[0]
    if '*' in ver_str:
        assert comp in ('>=', '==')
        assert (m := re.search('((?:\d\.)+)\*$', ver_str)), \
            'the asterisk symbol could only be in minor or patch position'
        comp = '>='  # noqa
        minor_or_patch = 'minor' if m.group(1).count('.') == 1 else 'patch'
        bottom_ver = semver.Version.parse(ver_str)
        if minor_or_patch == 'minor':
            bumped_ver = bottom_ver.bump_major()
        else:
            bumped_ver = bottom_ver.bump_minor()
        for ver in map(semver.Version.parse, candidates):
            if bottom_ver <= ver < bumped_ver:
                assert str(ver) in candidates
                return str(ver)
        else:
            return None
    else:
        assert comp in ('>=', '>', '==', '<', '<=')
        ver_str_0 = ver_str
        for ver_str_1 in candidates:
            if compare_version(ver_str_0, comp, ver_str_1):
                return ver_str_1
        else:
            return None
