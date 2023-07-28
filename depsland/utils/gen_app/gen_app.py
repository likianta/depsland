"""
ref: https://github.com/tfmoraes/macnolo
     docs/devnote/how-to-create-macos-app-bundle.md
"""
from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads
from lk_utils import xpath

from ...manifest import T


def gen_app(manifest: T.Manifest, path_o: str, icon: str = None) -> None:
    dir_i = xpath('template')
    dir_o = path_o
    assert dir_o.endswith('.app')
    
    fs.copy_tree(dir_i, dir_o, overwrite=True)
    
    _inplace(f'{dir_o}/Contents/Info.plist', {
        'APP_NAME': manifest['appid'],
    })
    
    fs.move(
        f'{dir_o}/Contents/MacOS/APP_NAME',
        f'{dir_o}/Contents/MacOS/{manifest["appid"]}'
    )
    _inplace(
        f'{dir_o}/Contents/MacOS/{manifest["appid"]}',
        {'APPID': manifest['appid'], 'VERSION': manifest['version']}
    )
    
    if icon:
        assert icon.endswith('.icns')
        fs.copy_file(
            icon, f'{dir_o}/Contents/Resources/{manifest["appid"]}.icns'
        )


def _create_plist() -> str:
    pass


def _inplace(file: str, placeholders: dict) -> None:
    data_i: str = loads(file, 'plain')
    data_o = data_i.format(**placeholders)
    dumps(data_o, file, 'plain')
