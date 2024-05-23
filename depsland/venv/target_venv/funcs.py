import typing as t

from lk_utils.textwrap import dedent

from .indexer import T as T0


# noinspection PyTypedDict
class T(T0):
    PackageRelations = t.Dict[T0.PackageName, t.Iterable[T0.PackageName]]


def expand_package_names(
    request_names: t.Iterable[T.PackageName], packages: T.Packages
) -> T.PackageRelations:  # returns dict[lead_name, iterable[dep_name]]
    def expanding(
        name: T.PackageName, _collector: t.Set[T.PackageName]
    ) -> t.Iterator[T.PackageName]:
        if name not in packages:
            print(':v4l', sorted(packages.keys()), name)
            print(
                ':v4',
                dedent('''
                    the requested package name "{}" is not found in the index
                    (see above list).
                    possible reasons:
                        - the name was misspelled.
                        - the name was not registered in the
                            "pyproject.toml"/"requirements.txt".
                        - if you were using "pyproject.toml", you may put the
                            package in `dev` section.
                ''').format(name),
            )
            raise KeyError(name)
        for dep_name in packages[name]['dependencies']:
            if dep_name not in _collector:
                yield dep_name
                _collector.add(dep_name)
                yield from expanding(dep_name, _collector)
    
    out = {}
    for name in request_names:
        out[name] = expanding(name, set())
    return out
