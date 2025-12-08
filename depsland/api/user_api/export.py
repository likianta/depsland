import os

from lk_utils import fs

from ... import paths
from ...manifest import T
from ...manifest import get_last_installed_version
from ...manifest import load_manifest
from ...pypi import pypi
from ...pypi import rebuild_pypi_index


def export_application(
    appid: str, version: str = None, root_o: str = None
) -> str:
    assert paths.project.project_mode != ''
    if version is None:
        version = get_last_installed_version(appid)
    dir_o = '{}/{}-{}'.format(root_o or paths.temp.make_dir(), appid, version)
    assert not fs.exist(dir_o)
    fs.make_dir(dir_o)
    
    manifest_file = '{}/{}/{}/manifest.pkl'.format(
        paths.apps.root, appid, version
    )
    manifest = load_manifest(manifest_file)
    
    _init_tree(dir_o)
    _copy_dependencies(dir_o, manifest)
    
    return dir_o


def share():
    pass  # TODO


def _init_tree(dir_o: str) -> None:
    root_i = paths.project.root
    root_o = dir_o
    
    # make empty dirs
    os.mkdir(f'{root_o}/apps')
    os.mkdir(f'{root_o}/apps/.bin')
    os.mkdir(f'{root_o}/apps/.venv')
    os.mkdir(f'{root_o}/build')
    os.mkdir(f'{root_o}/chore')
    # os.mkdir(f'{root_o}/config')
    # os.mkdir(f'{root_o}/depsland')
    os.mkdir(f'{root_o}/dist')
    os.mkdir(f'{root_o}/docs')
    os.mkdir(f'{root_o}/oss')
    os.mkdir(f'{root_o}/oss/apps')
    os.mkdir(f'{root_o}/oss/test')
    # os.mkdir(f'{root_o}/pypi')
    # os.mkdir(f'{root_o}/python')
    # os.mkdir(f'{root_o}/sidework')
    os.mkdir(f'{root_o}/temp')
    os.mkdir(f'{root_o}/temp/.self_upgrade')
    os.mkdir(f'{root_o}/temp/.unittests')
    
    # copy files and folders
    fs.make_link(
        f'{root_i}/build/exe',
        f'{root_o}/build/exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-cli.exe',
        f'{root_o}/apps/.bin/depsland.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui.exe',
        f'{root_o}/Depsland.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui-debug.exe',
        f'{root_o}/Depsland (Debug).exe',
    )
    fs.make_link(
        f'{root_i}/build/icon',
        f'{root_o}/build/icon',
    )
    # fs.copy_tree(
    #     f'{root_i}/build/setup_wizard',
    #     f'{root_o}/build/setup_wizard',
    # )
    fs.make_link(
        f'{root_i}/chore/pypi_blank',
        f'{root_o}/chore/pypi_blank',
    )
    fs.make_link(
        f'{root_i}/config',
        f'{root_o}/config',
    )
    fs.make_link(
        f'{root_i}/depsland',
        f'{root_o}/depsland',
    )
    fs.copy_tree(
        f'{root_i}/chore/pypi_blank',
        f'{root_o}/pypi'
    )
    fs.make_link(
        f'{root_i}/python',
        f'{root_o}/python',
    )
    fs.copy_tree(
        f'{root_i}/sidework',
        f'{root_o}/sidework',
    )
    # fs.copy_file(
    #     f'{root_i}/.depsland_project.json',
    #     f'{root_o}/.depsland_project.json',
    # )
    
    fs.dump(
        {'project_mode': 'production'},
        f'{root_o}/.depsland_project.json'
    )


def _copy_dependencies(dir_o: str, manifest: T.Manifest) -> None:
    pypi_dir = '{}/pypi'.format(dir_o)
    pypi_index = pypi.index
    info: T.PackageInfo
    for name, info in manifest['dependencies']:
        pkg_id = info['id']
        print(pkg_id)
        dl_path, ins_path = pypi_index[pkg_id]
        fs.make_link(
            dl_path,
            '{}/downloads/{}'.format(pypi_dir, fs.basename(dl_path))
        )
        fs.make_dir('{}/installed/{}'.format(pypi_dir, name))
        fs.make_link(
            ins_path,
            '{}/installed/{}/{}'.format(pypi_dir, name, info['version'])
        )
    id_2_paths, name_2_vers = rebuild_pypi_index(
        perform_pip_install=False,
        _save=False
    )
    fs.dump(id_2_paths, '{}/index/id_2_paths.json'.format(pypi_dir))
    fs.dump(name_2_vers, '{}/index/name_2_vers.json'.format(pypi_dir))
