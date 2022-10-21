import os
import typing as t
from ..downloader import download
from ..pip import pip
from ..utils import ziptool


class T:
    Config = t.TypedDict('Config', {
        'root'     : str,
        'resources': t.Dict[
            Dst := str,
            Src := str,
        ],
        'pypi'     : t.Dict[
            t.TypeAlias('Name', str),
            t.TypeAlias('VersionSpec', str)
        ]
    })


def main(config: T.Config) -> None:
    print(':l', config)
    
    root = config['root']
    # noinspection PyTypeChecker
    for dst, src in config['resources'].items():
        src = f'{root}/{src}'
        _download_and_unpack(dst, src)
    
    # noinspection PyTypeChecker
    for name, vspec in config['pypi'].items():
        pip.install(f'{name}{vspec.replace(" ", "")}')


def _download_and_unpack(dst: str, src: str) -> str:
    download(dst, src, overwrite=True)
    
    src_file = src
    src_dire = os.path.splitext(src)[0]
    ziptool.unzip_file(src_file, src_dire, overwrite=True)
    
    return src_dire
