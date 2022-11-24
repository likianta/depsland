import os
import typing as t

from lk_utils import fs

from .pypi import pypi
from ..paths import pypi as pypi_paths


class T:
    PackagesSize = t.NamedTuple('PackagesSize', (
        ('downloaded', t.Dict[str, int]),
        ('installed', t.Dict[str, int]),
    ))


def measure_package_size(
        name: str,
        version: str = None,
        include_dependencies=True
) -> T.PackagesSize:
    assert name in pypi.name_2_versions
    if version is None:
        version = pypi.name_2_versions[name][0]
    print('measuring package size', name, version)
    
    downloaded_size = 0
    installed_size = 0
    simple_count = 0
    out = T.PackagesSize(downloaded={}, installed={})
    
    calculated = set()
    
    def recurse_measure(name_id: str, indent: int):
        nonlocal downloaded_size, installed_size, simple_count
        
        simple_count += 1
        print('[dim]\\[{:>02d}][/]{}|- [cyan]{}[/]'.format(
            simple_count, '   ' * indent, name_id
        ), ':r')
        if name_id in calculated:
            return
        calculated.add(name_id)

        downloaded_path, installed_path = pypi.name_id_2_paths[name_id]
        #   the downloaded_path is a file.
        #   the installed_path is a directory.
        #   both are relative paths. be noted to convert them to absolute.
        
        downloaded_path, installed_path = (
            f'{pypi_paths.root}/{downloaded_path}',
            f'{pypi_paths.root}/{installed_path}'
        )
        
        size1 = _get_file_size(downloaded_path)
        size2 = _get_folder_size(installed_path)
        downloaded_size += size1
        installed_size += size2
        out.downloaded[name_id] = size1
        out.installed[name_id] = size2
        
        if include_dependencies:
            for nid in pypi.dependencies[name_id]:
                recurse_measure(nid, indent + 1)
    
    recurse_measure(f'{name}-{version}', 0)
    
    print('downloaded size:', _pretty_size(downloaded_size), ':v2')
    print('installed size:', _pretty_size(installed_size), ':v2')
    return out


def _get_file_size(file: str) -> int:
    return os.path.getsize(file)


def _get_folder_size(folder: str) -> int:
    return sum(os.path.getsize(x) for x in fs.findall_file_paths(folder))


def _pretty_size(size: int) -> str:
    if size < 1024:
        return f'{size}B'
    elif size < 1024 ** 2:
        return f'{size / 1024:.2f}KB'
    elif size < 1024 ** 3:
        return f'{size / 1024 ** 2:.2f}MB'
    else:
        return f'{size / 1024 ** 3:.2f}GB'
