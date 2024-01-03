import re
import typing as t

from lk_utils import loads

from ..normalization import VersionSpec
from ..normalization import normalize_name


class T:
    ExactVersion = str
    PackageId = str  # str['{name}-{version}']
    PackageName = str
    
    # noinspection PyTypedDict
    PackageInfo = t.TypedDict('PackageInfo', {
        'id'      : PackageId,
        'name'    : PackageName,
        'version' : ExactVersion,
        'appendix': t.TypedDict('Appendix', {
            'custom_url': str,
            'platform'  : t.Set[str],
            'python'    : t.List[VersionSpec],
        }, total=False)
    })
    
    # Packages = t.Dict[PackageId, PackageInfo]
    Packages = t.Dict[PackageName, PackageInfo]


class Regex:
    
    @staticmethod
    def simple_extract_name_and_version(
        text: str
    ) -> t.Tuple[T.PackageName, T.ExactVersion]:
        return t.cast(
            t.Tuple[T.PackageName, T.ExactVersion],
            re.match(r'(.+)==(.+)', text).groups()
        )


_regex = Regex()


def resolve_requirements_lock(file: str) -> T.Packages:
    out = {}
    for line in loads(file, 'plain').splitlines():
        if not line or line.startswith('# '):
            continue
        pkg = _resolve_line(line)
        # pid = '{}-{}'.format(pkg['name'], pkg['version'])
        out[pkg['name']] = pkg
    return out


def _resolve_line(line: str) -> T.PackageInfo:
    if ' ; ' in line:
        a, b = line.split(' ; ', 1)
        name, ver = _regex.simple_extract_name_and_version(a)
        name = normalize_name(name)
        marker: str
        platforms = set()
        pyverspecs = []
        for marker in re.split(r' and | or ', b):
            d, e, f = marker.split(' ')
            if d == 'python_version':
                pyverspecs.append(
                    VersionSpec(name=name, version=f, comparator=e)
                )
            elif d == 'sys_platform':
                assert e == '=='
                assert f in ('darwin', 'linux', 'win32')
                platforms.add('windows' if f == 'win32' else f)
            elif d == 'os_name':
                assert e == '=='
                assert f == 'nt'
                platforms.add('windows')
            else:
                raise Exception(line)
        return {
            'id'      : f'{name}-{ver}',
            'name'    : name,
            'version' : ver,
            'appendix': {
                'custom_url': b,
                'platform'  : platforms,
                'python'    : pyverspecs,
            }
        }
    
    elif ' @ ' in line:
        a, b = line.split(' ; ', 1)
        name, ver = _regex.simple_extract_name_and_version(a)
        name = normalize_name(name)
        return {
            'id'      : f'{name}-{ver}',
            'name'    : name,
            'version' : ver,
            'appendix': {
                'custom_url': b,
            }
        }
    
    else:
        name, ver = _regex.simple_extract_name_and_version(line)
        name = normalize_name(name)
        return {
            'id'      : f'{name}-{ver}',
            'name'    : name,
            'version' : ver,
            'appendix': {}
        }

# def _resolve_marker(marker: str):
#     pass
