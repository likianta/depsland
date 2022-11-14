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
    
    is_only_one_spec = len(verspecs) == 1
    
    filtered_candidates = []
    for spec in verspecs:
        for candidate in candidates:
            if spec.version == '' or compare_version(
                    candidate, spec.comparator, spec.version):
                if is_only_one_spec:
                    return candidate
                filtered_candidates.append(candidate)
        if filtered_candidates:
            candidates = filtered_candidates
            filtered_candidates = []
        else:
            return None
    # assert filtered_candidates == [] and candidates == [...]
    return candidates[0]


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


# DELETE: seldomly used.
def sort_versions(
        versions: t.List[str],
        reverse: bool,
) -> None:
    versions.sort(
        key=lambda x: semver_parse(x),
        reverse=reverse
    )


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
