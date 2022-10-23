import os
import typing as t
from lk_utils import loads, fs
from uuid import uuid1
from .. import paths
from ..downloader import download
from ..utils import ziptool


class T:
    Manifest = t.TypedDict('Manifest', {
        'name'        : str,
        'version'     : str,
        'assets'      : dict[(Url := str), (Relpath := str)],
        'dependencies': dict[(Name := str), (VersionSpec := str)],
    })


def main(url):
    """
    depsland install <url>
    """
    dire_o = f'{paths.temp_dir}/{uuid1().hex}'
    os.mkdir(dire_o)
    download(url, manifest_file := f'{dire_o}/manifest.json')
    manifest: T.Manifest = loads(manifest_file)
    print(':v2', manifest['name'], manifest['version'])

    # -------------------------------------------------------------------------
    
    dire_i = dire_o
    dire_o = '{}/{}/{}'.format(
        paths.apps_dir,
        manifest['name'],
        manifest['version']
    )
    
    if os.path.exists(dire_o):
        # FIXME: ask user turn to upgrade or force-reinstall command.
        raise FileExistsError(dire_o)
    
    # assets
    paths_to_be_generated = set(
        fs.normpath(f'{dire_o}/{x}')
        for x in manifest['assets'].values()  # noqa
    )
    [os.makedirs(x, exist_ok=True) for x in paths_to_be_generated]
    for url, relpath in manifest['assets'].items():  # noqa
        download(url, f'{dire_o}/{relpath}')
