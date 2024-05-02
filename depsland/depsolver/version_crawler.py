"""
crawl versions of a package from pypi.
notice: internet connection is required.
"""
from json import loads as json_loads
from urllib import request


def get_latest_version(name: str) -> str:
    """
    crawl versions from deps.dev
    the format: https://deps.dev/_/s/pypi/p/<package_name>/v/
    response: {
        'package': {'system': 'PyPI', 'name': package_name},
        'defaultVersion': str, ...
    }
    """
    url = f'https://deps.dev/_/s/pypi/p/{name}/v/'
    with request.urlopen(url) as f:
        return json_loads(f.read())['defaultVersion']


def get_all_versions(name: str):
    pass
