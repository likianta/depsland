import json
import typing as t

from lk_utils import fs
from lk_utils import run_cmd_args

# from .requirements_lock import T as T0
from .. import paths
from .. import utils
from ..normalization import normalize_name
from ..pypi import pypi

index = pypi.index


class T:
    # fmt:off
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
    # fmt:on
    # Dependencies1 = t.Iterator[t.Tuple[str, str]]  # ((name, version), ...)
    # Dependencies1 = t.Dict[str, str]
    Dependencies1 = t.Dict[str, dict]  # see T0.Packages


# TODO
def resolve_dependencies(deps0: T.Dependencies0) -> T.Dependencies1:
    if not deps0:  # None, empty dict/list/string/etc.
        return {}
    
    out = {}
    
    if isinstance(deps0, str):
        pass
    
    elif isinstance(deps0, list):
        raw_requirements = '\n'.join(deps0)
        hash = utils.get_content_hash(raw_requirements)[::4]  # 8 chars
        print(f'snapdep/{hash}.lock')
        lock_file = f'{paths.pypi.snapdep}/{hash}.lock'
        if not fs.exists(lock_file):
            print('building dependencies tree, this may take a while', ':t2s')
            dir_m = utils.make_temp_dir()
            fs.dump(raw_requirements, f'{dir_m}/requirements.txt')
            json_data = run_cmd_args(
                'pipgrip', '--json', '--sort',
                ('-r', 'requirements.txt'),
                ('--cache-dir', paths.pypi.cache),
                ('--index-url', 'https://pypi.tuna.tsinghua.edu.cn/simple'),
                cwd=dir_m,
                verbose=False,
            )
            requirements = []
            for k, v in json.loads(json_data).items():
                requirements.append('{}=={}'.format(
                    normalize_name(k), v
                ))
            fs.dump(requirements, lock_file)
            print('requirements get locked', hash, ':t2')
        for line in fs.load(lock_file).splitlines():
            name, ver = line.split('==', 1)
            # out[name] = ver
            out[name] = {
                'id'      : f'{name}-{ver}',
                'name'    : name,
                'version' : ver,
                'appendix': None,
            }
    
    elif isinstance(deps0, dict):
        pass
    
    return out
