"""
ref: https://github.com/tfmoraes/macnolo
     docs/devnote/how-to-create-macos-app-bundle.md
"""
import re

from lk_utils import fs

from .... import paths
from ....manifest import T


# FIXME: not ready to use
def make_app(manifest: T.Manifest, dir_o: str, icon: str = None) -> str:
    assert dir_o.endswith('.app')
    dir_i = fs.xpath('template')
    
    fs.copy_tree(dir_i, dir_o, overwrite=True)
    
    # inplace `Info.plist`
    _inplace(
        f'{dir_o}/Contents/Info.plist', {
            'APP_NAME': manifest['name'],
            'APP_ID': manifest['appid'],
            'APP_VERSION': manifest['version'],
            'APP_VERSION_SHORT':
                re.match(r'\d+\.\d+', manifest['version']).group(0),
            'DEV_ID': 'dev.likianta',
        }
    )
    
    # inplace `APP_NAME`
    fs.move(
        f'{dir_o}/Contents/MacOS/APP_NAME',
        f'{dir_o}/Contents/MacOS/{manifest["appid"]}'
    )
    _inplace(
        f'{dir_o}/Contents/MacOS/{manifest["appid"]}',
        {
            'DEPSLAND_DIR': paths.project.root,  # TEST
            'APPID': manifest['appid'],
            'VERSION': manifest['version'],
        }
    )
    
    # add icon
    if not icon:
        icon = paths.build.launcher_icon
    assert icon.endswith('.icns')
    fs.copy_file(icon, f'{dir_o}/Contents/Resources/{manifest["appid"]}.icns')
    
    return f'{dir_o}/Contents/Resources'


_re_placeholder = re.compile(r'\$(\w+)')


def _inplace(file: str, placeholders: dict) -> None:
    data_i: str = fs.load(file, 'plain')
    data_o = _re_placeholder.sub(lambda m: placeholders[m.group(1)], data_i)
    fs.dump(data_o, file, 'plain')
