import os
import typing as t
from lk_utils import fs
from lk_utils import loads
from uuid import uuid1
from ... import paths
from ...downloader import download
from ...pip import pip
from ...utils import ziptool


class T:
    Manifest = t.TypedDict('Manifest', {
        'name'        : str,
        'version'     : str,
        'assets'      : dict[(Url := str), (Relpath := str)],
        'dependencies': dict[(Name := str), (VersionSpec := str)],
    })


def main(url: str) -> str:
    """
    depsland install <url>
    """
    link_i: str = url
    dire_m: str = f'{paths.temp_dir}/{uuid1().hex}'  # intermediate directory
    dire_o: str
    
    os.mkdir(dire_m)
    
    # download manifest
    manifest_file = f'{dire_m}/manifest.json'
    download(link_i, manifest_file)
    manifest: T.Manifest = loads(manifest_file)
    print(':v2', manifest['name'], manifest['version'])
    
    # check dire_o
    dire_o = '{}/{}/{}'.format(
        paths.apps_dir,
        manifest['name'],
        manifest['version']
    )
    if os.path.exists(dire_o):
        # FIXME: ask user turn to upgrade or reinstall command.
        raise FileExistsError(dire_o)
    
    # assets (make dirs)
    paths_to_be_generated = set(
        fs.normpath(f'{dire_m}/{x}')
        for x in manifest['assets'].values()  # noqa
    )
    paths_to_be_generated = set(
        x for x in paths_to_be_generated if fs.isdir(x)
    )
    [os.makedirs(x, exist_ok=True) for x in paths_to_be_generated]
    
    # assets (download)
    for url, relpath in manifest['assets'].items():  # noqa
        file_m = fs.normpath(f'{dire_m}/{relpath}')
        _download_and_unpack(url, file_m)
    
    # dependencies
    for name, vspec in manifest['dependencies'].items():  # noqa
        pip.install(f'{name}{vspec.replace(" ", "")}')
    
    # move to final directory
    fs.move(dire_m, dire_o)
    return dire_o


def _download_and_unpack(dst: str, src: str) -> None:
    download(dst, src, overwrite=True)
    src_file = src
    src_dire = os.path.splitext(src)[0]
    ziptool.unzip_file(src_file, src_dire, overwrite=True)
