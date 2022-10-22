from collections import defaultdict
from os.path import exists
from re import compile

from lk_logger import lk
from lk_utils import dumps
from lk_utils import loads
from lk_utils import send_cmd
from .normalization import normalize_name
from .paths import pypi_dir
from .typehint import TPip


def full_indexing(pip: TPip):
    f1 = f'{pypi_dir}/index/name_versions.pkl'
    f2 = f'{pypi_dir}/index/locations.pkl'
    f3 = f'{pypi_dir}/index/dependencies.pkl'
    if all(map(exists, (f1, f2, f3))):
        name_versions = loads(f1)
        locations = loads(f2)
        dependencies = loads(f3)
    else:
        name_versions = dict()
        locations = defaultdict(list)
        dependencies = defaultdict(list)
    
    for name, version in _get_list(pip.head):
        lk.logax(name, version)
        if name in name_versions and version == name_versions[name]:
            continue
        name_versions[name] = version
        dependencies[name].extend(sorted(pip.show_dependencies(name)))
        locations[name].extend(sorted(pip.show_locations(name)))
    
    dumps(name_versions, f1)
    dumps(locations, f2)
    dumps(dependencies, f3)
    # for human readability
    dumps(name_versions, f1.replace('.pkl', '.json'), pretty_dump=True)
    dumps(locations, f2.replace('.pkl', '.json'), pretty_dump=True)
    dumps(dependencies, f3.replace('.pkl', '.json'), pretty_dump=True)


def _get_list(pip_head):
    pattern = compile(r'([^ ]+) +(.+)')
    
    ret = send_cmd(f'{pip_head} list')
    
    for i, line in enumerate(ret.splitlines()):
        if i == 0 or i == 1:
            continue
        name, version = pattern.search(line).groups()
        # yield name, version
        yield normalize_name(name), version
