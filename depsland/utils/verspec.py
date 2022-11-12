import re
import typing as t

import semver  # https://github.com/python-semver/python-semver

from ..normalization import T
from ..normalization import VersionSpec
from ..normalization import normalize_name
from ..normalization import normalize_version_spec


def compare_version(v0: str, comp: str, v1: str, _patch=True) -> bool:
    """
    args:
        comp: '>', '>=', '==', '<=', '<'
    """
    if _patch:
        v0, v1 = map(_minor_fix_version_form, (v0, v1))
    r: int = semver.compare(v0, v1)  # -1, 0, 1
    return eval(f'r {comp} 0', {'r': r})


def find_proper_version(
        *verspecs: VersionSpec,
        candidates: t.Sequence[T.Version]
) -> t.Optional[str]:
    """
    args:
        request: ('1.2.3', '>=')
        candidates: a sorted list of version strings, from new to old.
    """
    assert len(verspecs)
    if not candidates:
        return None
    if len(verspecs) == 1 and verspecs[0].version == '':
        return candidates[0]
    
    filtered_candidates = []
    for spec in verspecs:
        for candidate in candidates:
            if compare_version(candidate, spec.comparator, spec.version):
                if len(verspecs) == 1:
                    return candidate
                filtered_candidates.append(candidate)
        if filtered_candidates:
            candidates = filtered_candidates
            filtered_candidates = []
        else:
            return None
    assert filtered_candidates
    # print(':v', filtered_candidates)
    return filtered_candidates[0]


def get_name_and_version_from_filename(filename: str) -> t.Tuple[str, str]:
    """
    examples:
        'PyYAML-6.0-cp310-cp310-macosx_10_9_x86_64.whl' -> ('PyYAML', '6.0')
        'lk-logger-4.0.7.tar.gz' -> ('lk-logger', '4.0.7')
        'aliyun-python-sdk-2.2.0.zip' -> ('aliyun-python-sdk', '2.2.0')
    """
    for ext in ('.whl', '.tar.gz', '.zip'):
        if filename.endswith(ext):
            filename = filename.removesuffix(ext)
            break
    else:
        raise ValueError(filename)
    
    # assert ext
    if ext == '.whl':
        a, b, _ = filename.split('-', 2)
    else:
        a, b = filename.rsplit('-', 1)
    return a, b


def get_verspec_from_filename(filename: str) -> VersionSpec:
    a, b = get_name_and_version_from_filename(filename)
    name = normalize_name(a)
    # -> 'pyside6'
    verspec_ = tuple(normalize_version_spec(name, b))
    assert len(verspec_) == 1
    verspec = verspec_[0]
    # -> VersionSpec<'pyside6==6.0.0'>
    return verspec


def semver_parse(ver: str) -> semver.Version:
    ver = _minor_fix_version_form(ver)
    return semver.Version.parse(ver)


# TODO (refactor) or DELETE
def sort_versions(versions: t.List[T.Version], reverse=True):
    """
    References:
        Sort versions in Python:
            https://stackoverflow.com/questions/12255554/sort-versions-in-python
            /12255578
        The LooseVersion and StrictVersion difference:
            https://www.python.org/dev/peps/pep-0386/
    """
    
    def _normalize_version(v: t.Union[str, T.Version]):
        # TODO: the incoming `param:v` type must be TVersion; TNameId should be
        #   removed.
        if '-' in v:
            v = v.split('-', 1)[-1]
        if v in ('', '*', 'latest'):
            return '999999.999.999'
        else:
            return v
    
    versions.sort(
        key=lambda v: semver_parse(_normalize_version(v)),
        # `x` type is Union[TNameId, TVersion], for TNameId we
        # need to split out the name part.
        reverse=reverse
    )
    return versions


def _minor_fix_version_form(raw_verspec: str) -> str:
    """
    examples:
        335             335.0.0
        1.7             1.7.0
        1.0.0b3         1.0.0-b.3
        0.12.0.post2    0.12.0-post.2
        6.4.0.1         6.4.0-1
    see unittest in `unittests/raw_version_to_semver.py`
    """
    if raw_verspec.isdigit():
        return f'{raw_verspec}.0.0'
    elif raw_verspec.replace('.', '', 1).isdigit():
        return f'{raw_verspec}.0'
    pattern = re.compile(r'^(\d+\.\d+\.\d+)\.?((?:[a-zA-Z]+)?)(\d+)')
    #                       ^~~~~~~~~~~~~~1   ^~~~~~~~~~~~~~~2^~~~3
    if pattern.search(raw_verspec):
        raw_verspec = pattern.sub(
            lambda m: '{}-{}.{}'.format(*m.groups()), raw_verspec
        ).replace('-.', '-')
    return raw_verspec
