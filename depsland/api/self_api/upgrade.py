from lk_utils import fs

from ..user_api import install_by_appid
from ... import paths
from ...manifest import load_manifest


def self_upgrade() -> str:
    dir_i = install_by_appid('depsland')
    dir_o = fs.abspath('{}/../{}'.format(paths.project.root, fs.dirname(dir_i)))
    manifest = load_manifest(f'{dir_i}/manifest.pkl')
    
    fs.move(dir_i, dir_o)
    fs.move(
        '{}/depsland/{}'.format(paths.apps.venv, manifest['version']),
        f'{dir_o}/chore/site_packages'
    )
    fs.remove_file(f'{dir_o}/Depsland Standalone.exe')
    fs.remove_file(f'{dir_o}/Depsland Standalone (Debug).exe')
    fs.copy_file(
        f'{dir_o}/build/exe/depsland-cli.exe',
        f'{dir_o}/apps/.bin/depsland.exe',
        True
    )
    fs.copy_file(
        f'{dir_o}/build/exe/depsland-gui.exe',
        f'{dir_o}/Depsland.exe',
        True
    )
    fs.copy_file(
        f'{dir_o}/build/exe/depsland-gui-debug.exe',
        f'{dir_o}/Depsland (Debug).exe',
        True
    )
    fs.dump(
        {'project_mode': 'production'},
        f'{dir_o}/.depsland_project.json'
    )
    fs.make_link(paths.apps.root, f'{dir_o}/apps', True)
    fs.make_link(paths.pypi.root, f'{dir_o}/pypi', True)
    fs.make_link(paths.python.root, f'{dir_o}/python', True)
    fs.make_link(dir_o, '{}/../current'.format(paths.project.root), True)
    
    return dir_o
