import re
import typing as t

import semver  # https://github.com/python-semver/python-semver

from .normalization import T
from .normalization import VersionSpec
from .normalization import split_filename_of_package
from .normalization import normalize_verspecs


def compare_version(v0: str, comp: str, v1: str, _patch: bool = True) -> bool:
    """
    args:
        comp: '>', '>=', '==', '<=', '<'
    """
    if _patch:
        v0, v1 = map(_minor_fix_version_form, (v0, v1))
    r: int = semver.compare(v0, v1)  # -1, 0, 1
    return eval(f'r {comp} 0', {'r': r})


def findone_eligible_version(
    verspecs: t.Sequence[VersionSpec],
    candidates: t.Sequence[T.Version],
) -> t.Optional[T.Version]:
    for one in findall_eligible_versions(verspecs, candidates):
        return one
    return None


def findall_eligible_versions(
    verspecs: t.Sequence[VersionSpec],
    candidates: t.Sequence[T.Version],
) -> t.Iterator[T.Version]:
    """
    params:
        candidates: a sorted list of version strings, from new to old.
            see also `depsland.pypi.index.T.Name2Versions`
    """
    if not candidates:
        return
    if not verspecs:
        yield from candidates
        return
    for candidate in candidates:
        for spec in verspecs:
            if spec.version == '' or compare_version(
                candidate, spec.comparator, spec.version
            ):
                yield candidate


# DELETE
def find_proper_version(
    verspecs: t.Sequence[VersionSpec],
    candidates: t.Sequence[T.Version],
) -> t.Optional[str]:
    """
    params:
        candidates: a sorted list of version strings, from new to old.
            see also `depsland.pypi.index.T.Name2Versions`
    note: if `verspecs` is empty, return the latest version of candidates.
    """
    if not candidates: return None
    if not verspecs: return candidates[0]
    
    has_only_one_spec = len(verspecs) == 1
    filtered_candidates = []
    for spec in verspecs:
        for candidate in candidates:
            if spec.version == '' or compare_version(
                    candidate, spec.comparator, spec.version):
                if has_only_one_spec:
                    return candidate
                filtered_candidates.append(candidate)
        if filtered_candidates:
            candidates = filtered_candidates
            filtered_candidates = []
        else:
            return None
    # assert filtered_candidates == [] and candidates == [...]
    return candidates[0]


def get_verspec_from_filename(filename: str) -> VersionSpec:
    name, ver = split_filename_of_package(filename)
    verspecs = tuple(normalize_verspecs(name, ver))
    assert len(verspecs) == 1
    verspec = verspecs[0]
    # -> VersionSpec<'pyside6==6.0.0'>
    return verspec


def semver_parse(ver: str) -> semver.Version:
    ver = _minor_fix_version_form(ver)
    return semver.Version.parse(ver)


def sort_versions(versions: t.List[str], reverse: bool = True) -> None:
    if versions and len(versions) > 1:
        versions.sort(key=semver_parse, reverse=reverse)


def _minor_fix_version_form(raw_verspec: str) -> str:
    """
    examples:
        335             335.0.0
        1.7             1.7.0
        1.0.0b3         1.0.0-b.3
        0.12.0.post2    0.12.0-post.2
        6.4.0.1         6.4.0-1
        21.7b0          21.7.0-b.0
    see unittest in `unittests/raw_version_to_semver.py`
    """
    pattern1 = re.compile(r'^(\d+(?:\.\d+)?(?:\.\d+)?)(.*)')
    main, sub = pattern1.search(raw_verspec).groups()
    
    if main.isdigit():
        main = f'{main}.0.0'
    elif main.replace('.', '', 1).isdigit():
        main = f'{main}.0'
    
    if sub:
        if sub.startswith('.'):
            sub = sub.lstrip('.')
        pattern2 = re.compile(r'([a-zA-Z]+)(\d+)')
        if pattern2.search(sub):
            sub = pattern2.sub(lambda x: '.'.join(x.groups()), sub)
        sub = f'-{sub}'
    
    return main + sub
