import typing as t
import re

from . import version_crawler
from .requirements_lock import T as T0
from .. import normalization as norm
from .. import verspec
from ..normalization import normalize_anyname
from ..pypi import pypi

index = pypi.index


class T:
    Dependencies0 = t.Union[
        # 1. no dependency
        None,
        # 2. a file path, usually 'pyproject.toml', 'requirements.txt', etc.
        str,
        # 3. a list of packages. e.g. ['requests', 'numpy>=1.26', ...]
        t.List[str],
        # 4. packages with more detailed definitions. e.g.
        #   {
        #       'numpy': [
        #           {'version': '1.26.2', 'platform': 'linux'},
        #           {'version': '*', 'platform': '!=linux'},
        #       ], ...
        #   }
        t.Dict[str, t.Union[str, dict, list]],
    ]
    Dependencies1 = T0.Packages


def resolve_dependencies(deps0: T.Dependencies0) -> T.Dependencies1:
    if not deps0:  # None, empty dict/list/string/etc.
        return {}
    
    out = {}
    
    if isinstance(deps0, str):
        pass
    
    elif isinstance(deps0, list):
        for x in deps0:
            name, verspecs = normalize_anyname(x)
            if name in index.name_2_vers:
                proper_ver = verspec.find_proper_version(
                    verspecs, candidates=index.name_2_vers[name]
                )
                if not proper_ver:
                    pass  # raise error or refresh index from internet
            else:  # request from internet
                if verspecs:
                    pass
                else:
                    proper_ver = version_crawler.get_latest_version(name)
            out[name] = {
                'id': f'{name}-{proper_ver}',
                'name': name,
                'version': proper_ver,
                'appendix': None
            }
    
    elif isinstance(deps0, dict):
        pass
    
    return out
