import os.path
import typing as t

from .index import T as T0


# noinspection PyTypedDict
class T(T0):
    NameIdsGraph = t.Dict[T0.NameId, t.Tuple[T0.NameId, ...]]
    PathToPackage = t.TypedDict('DependencyAsset', {
        'type': t.Literal['bin', 'dir', 'file'],
        'hash': str,
        'source': t.TypedDict('Source', {
            'name': T0.PkgName,
            'version': T0.ExactVersion,
            'url': str,
        })
    })
    '''
    example:
        lib/site-packages
        |= yaml
            PathToPackage:
                type: dir
                hash: <str>  # can be evaluated by \
                #   `PyYAML-6.0.1.dist-info/RECORD`.
                source:
                    name: pyyaml  # lower case with hyphens connected.
                    #   the relation between `yaml` and `pyyaml` can be \
                    #   deduced by the path list from \
                    #   `PyYAML-6.0.1.dist-info/RECORD`.
                    version: 6.0.1  # from `PyYAML-6.0.1.dist-info`.
                    url: str  # usually it is an empty string. if there is a \
                    #   `direct_url.json` file in the \
                    #   `PyYAML-6.0.1.dist-info`, then extract the `url` field \
                    #   from it.
    '''
    PackagePaths = t.Dict[T0.TopName, PathToPackage]


def expand_dependencies(
    request_name_ids: t.Iterable[T.NameId], deps: T.DepsMap
) -> T.NameIdsGraph:
    def recurse(
        name_id: T.NameId, temp_holder: t.Set[T.NameId]
    ) -> t.Iterator[T.NameId]:
        for sub in deps[name_id]['dependencies']:
            if sub not in temp_holder:
                yield sub
                temp_holder.add(sub)
                yield from recurse(sub, temp_holder)
    
    out = {}
    for name_id in request_name_ids:
        out[name_id] = tuple(sorted(recurse(name_id, set())))
    return out


def reverse_mapping(root: str, deps: T.DepsMap) -> T.PackagePaths:
    """
    from (e.g.):
        lk_utils:
            name: lk_utils-2.6.0b4
            version: 2.6.0b4
            ...
            paths:
                - lk_utils
                - lk_utils-2.6.0b4.dist-info
                - bin/lk_utils
    to:
        lk_utils:
            type: dir
            hash: ...
            source:
                name: lk_utils
                version: 2.6.0b4
                url: ...
        lk_utils-2.6.0b4.dist-info:
            type: dir
            ...
        bin/lk_utils:
            type: bin
            ...
    """
    out: T.PackagePaths = {}
    for pkg_name, v0 in deps.items():
        for top_name in v0['paths']:
            out[top_name] = {
                'type': (
                    'bin' if top_name.startswith('bin/') else
                    'dir' if os.path.isdir(f'{root}/{top_name}') else 'file'
                ),
                'hash': v0['hash'],
                'source': {
                    'name': pkg_name,
                    'version': v0['version'],
                    'url': v0['url'],
                }
            }
    return out
