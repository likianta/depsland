import semver  # https://github.com/python-semver/python-semver
import typing as t
from ..normalization import T
from ..normalization import VersionSpec
from ..normalization import normalize_name
from ..normalization import normalize_version_spec


def compare_version(v0: str, comp: str, v1: str) -> bool:
    """
    args:
        comp: '>=', '>', '==', '<', '<='
    """
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
            if compare_version(spec.version, spec.comparator, candidate):
                if len(verspecs) == 1:
                    return candidate
                filtered_candidates.append(candidate)
        if filtered_candidates:
            candidates = filtered_candidates
            filtered_candidates = []
        else:
            return None
    assert filtered_candidates
    return filtered_candidates[0]


def get_verspec_from_filename(filename: str) -> VersionSpec:
    # e.g. 'PySide6-6.0.0-cp39-cp39-win_amd64.whl'
    a, b, _ = filename.split('-', 2)
    # -> ['PySide6', '6.0.0', 'cp39-cp39-win_amd64.whl']
    name = normalize_name(a)
    # -> 'pyside6'
    verspec_ = tuple(normalize_version_spec(name, b))
    assert len(verspec_) == 1
    verspec = verspec_[0]
    # -> VersionSpec<'pyside6==6.0.0'>
    return verspec


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
    
    versions.sort(key=lambda v: semver.Version.parse(_normalize_version(v)),
                  # `x` type is Union[TNameId, TVersion], for TNameId we
                  # need to split out the name part.
                  reverse=reverse)
    return versions
