import json
import typing as t
from functools import cache

from lk_utils import fs
from lk_utils import run_cmd_args

from .poetry_lock_resolver_2 import resolve_poetry_lock
from .requirements_lock import resolve_requirements_lock
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


@cache
def resolve_dependencies(
    deps0: T.Dependencies0, proj_dir: str
) -> T.Dependencies1:
    if not deps0:  # None, empty dict/list/string/etc.
        return {}
    
    if isinstance(deps0, str):
        assert deps0 in ('poetry.lock', 'pyproject.toml', 'requirements.lock')
        specfile = f'{proj_dir}/{deps0}'
    else:
        specfile = None
    lock_file = _get_snapshot_file(specfile or deps0)
    # raise Exception
    if fs.exists(lock_file):
        return fs.load(lock_file)
    
    print(
        'the first time building dependencies tree, this may take a while...',
        ':t2v3s'
    )
    
    if isinstance(deps0, str):  # a file
        # assert deps0 in ('poetry.lock', 'pyproject.toml', 'requirements.lock')
        assert all(map(fs.exists, (
            a := f'{proj_dir}/pyproject.toml',
            b := f'{proj_dir}/poetry.lock',
            c := f'{proj_dir}/{deps0}',
        )))
        if deps0 == 'requirements.lock':
            out = resolve_requirements_lock(a, b, c)
        else:  # NOTE (2024-07-01): currently this is mainly used.
            out = resolve_poetry_lock(a, b)
        fs.dump(out, lock_file)
        return out
    
    elif isinstance(deps0, list):
        raw_requirements = '\n'.join(deps0)
        dir_m = utils.make_temp_dir()
        fs.dump(raw_requirements, f'{dir_m}/requirements.txt')
        json_data = run_cmd_args(
            'pipgrip', '--json', '--sort',
            ('-r', 'requirements.txt'),
            # ('--cache-dir', paths.pypi.cache),
            ('--index-url', 'https://pypi.tuna.tsinghua.edu.cn/simple'),
            cwd=dir_m,
            verbose=False,
        )
        requirements = []
        for k, v in json.loads(json_data).items():
            requirements.append('{}=={}'.format(
                normalize_name(k), v
            ))
        out = {}
        for line in requirements:
            name, ver = line.split('==', 1)
            # out[name] = ver
            out[name] = {
                'id'      : f'{name}-{ver}',
                'name'    : name,
                'version' : ver,
                'appendix': None,
            }
    
    elif isinstance(deps0, dict):  # TODO
        raise NotImplementedError
    
    else:
        raise Exception
    
    fs.dump(out, lock_file)
    return out


def _get_snapshot_file(deps0: T.Dependencies0) -> str:
    if isinstance(deps0, str):
        hash = utils.get_file_hash(deps0)[::4]  # 8 chars
    elif isinstance(deps0, list):
        raw_requirements = '\n'.join(deps0)
        hash = utils.get_content_hash(raw_requirements)[::4]  # 8 chars
    elif isinstance(deps0, dict):
        raise NotImplementedError
    else:
        raise Exception
    
    print(f'snapdep/{hash}.pkl', ':p')
    lock_file = f'{paths.pypi.snapdep}/{hash}.pkl'
    return lock_file
