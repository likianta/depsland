import re
import typing as t
from collections import defaultdict

from lk_utils import fs
from lk_utils import loads

from ..normalization import normalize_name
from ..normalization import normalize_version_spec
from ..utils.verspec import semver_parse


def create_from_file(dst_dir: str, requirements_file: str) -> None:
    create_venv(dst_dir, _load_requirements(requirements_file))


def _load_requirements(file: str) -> t.Iterator[t.Tuple[str, str]]:
    pattern = re.compile(r'([-\w]+)(.*)')
    for line in loads(file).splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            name, ver = pattern.search(line).groups()
            ver = ver.replace(' ', '')
            yield name, ver


def create_venv(
        dst_dir: str,
        requirements: t.Iterable[t.Tuple[str, str]]
) -> None:
    from ..pypi import pypi
    
    fs.make_dir(dst_dir)
    
    packages = {}
    for raw_name, raw_vspec in requirements:
        name = normalize_name(raw_name)
        vspecs = tuple(normalize_version_spec(name, raw_vspec))
        packages[name] = vspecs
    print(':vl', packages)
    
    name_ids = pypi.install(packages, include_dependencies=True)
    name_ids = tuple(dict.fromkeys(name_ids))  # deduplicate and remain sequence
    name_ids = _resolve_conflicting_name_ids(name_ids)
    pypi.save_indexes()
    pypi.linking(sorted(name_ids), dst_dir)


def _resolve_conflicting_name_ids(name_ids: t.Iterable[str]) -> t.Iterable[str]:
    """
    if there are multiple versions for one name, for example 'lk_utils-2.4.1'
    and 'lk_utils-2.5.0', remain the most latest version.
    FIXME: this may not be a good idea, better to raise an error right once.
    """
    name_2_versions = defaultdict(list)
    for nid in name_ids:
        a, b = nid.split('-', 1)
        name_2_versions[a].append(b)
    if conflicts := {k: v for k, v in name_2_versions.items() if len(v) > 1}:
        print('found {} conflicting name ids'.format(len(conflicts)),
              conflicts, ':lv3')
        for v in conflicts.values():
            v.sort(key=lambda x: semver_parse(x), reverse=True)
        return (f'{k}-{v[0]}' for k, v in name_2_versions.items())
    else:
        return name_ids
