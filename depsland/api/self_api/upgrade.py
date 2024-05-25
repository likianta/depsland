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
        '{}/{}'.format(paths.apps.venv, manifest['version']),
        f'{dir_o}/chore/site_packages'
    )
    fs.make_link(paths.apps.root, f'{dir_o}/apps', True)
    fs.make_link(paths.pypi.root, f'{dir_o}/pypi', True)
    fs.make_link(paths.python.root, f'{dir_o}/python', True)
    fs.make_link(dir_o, '{}/../current'.format(paths.project.root), True)
    
    return dir_o
