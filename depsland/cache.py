import typing as tp
from collections import defaultdict

from lk_utils import fs

from .paths import cache as cache_paths

_cached_results = defaultdict(dict)


def cache(namespace: str) -> tp.Callable:
    def wrapper(func: tp.Callable) -> tp.Callable:
        def call(folder: str) -> tp.Any:
            if folder in _cached_results[namespace]:
                return _cached_results[namespace][folder]
            else:
                result = func(folder)
                _cached_results[namespace][folder] = result
                return result

        return call

    return wrapper


def clear_cache(namespace: str) -> None:
    _cached_results[namespace].clear()


def reset_cache(namespace: str, key: str, value: tp.Any) -> None:
    _cached_results[namespace][key] = value


# ------------------------------------------------------------------------------

_persistent_kv = fs.load(cache_paths.persistent_kv_pairs, default={})


def check_persistent_key_changed(key: str, val: tp.Any) -> bool:
    return val == _persistent_kv.get(key, None)


def save_persistent_key(key: str, val: tp.Any) -> None:
    if val != _persistent_kv.get(key, None):
        _persistent_kv[key] = val
        fs.dump(_persistent_kv, cache_paths.persistent_kv_pairs)
