import os.path
import typing as t

from .indexer import T as T0


# noinspection PyTypedDict
class T(T0):
    PackageRelations = t.Dict[T0.PackageName, t.Tuple[T0.PackageName, ...]]
    # DELETE
    PathToPackage = t.TypedDict(
        'DependencyAsset',
        {
            'type': t.Literal['bin', 'dir', 'file'],
            'hash': str,
            'source': t.TypedDict(
                'Source',
                {
                    'name': T0.PackageName,
                    'version': T0.ExactVersion,
                    'url': str,
                },
            ),
        },
    )
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
    PackagePaths = t.Dict[T0.PathName, PathToPackage]


def expand_package_names(
    request_names: t.Iterable[T.PackageName], packages: T.Packages
) -> T.PackageRelations:
    def recurse(
        name: T.PackageName, temp_holder: t.Set[T.PackageName]
    ) -> t.Iterator[T.PackageName]:
        for dep_name in packages[name]['dependencies']:
            if dep_name not in temp_holder:
                yield dep_name
                temp_holder.add(dep_name)
                yield from recurse(dep_name, temp_holder)
    
    out = {}
    for name in request_names:
        out[name] = tuple(sorted(recurse(name, set())))
    return out


# DELETE
def paths_2_package(root: str, deps: T.Packages) -> T.PackagePaths:
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
                    'bin'
                    if top_name.startswith('bin/')
                    else (
                        'dir'
                        if os.path.isdir(f'{root}/{top_name}')
                        else 'file'
                    )
                ),
                'hash': v0['hash'],
                'source': {
                    'name': pkg_name,
                    'version': v0['version'],
                    'url': v0['url'],
                },
            }
    return out
