import os
import typing as t

from argsense import CommandLineInterface
from lk_utils import fs
from lk_utils import loads

from ..dev_api.upload import T as T0
from ... import config
from ... import paths
from ...manifest import init_manifest
from ...manifest import load_manifest
from ...normalization import normalize_name
from ...normalization import normalize_version_spec
from ...oss import Oss
from ...oss import OssPath
from ...oss import get_oss_client
from ...pypi import pypi
from ...utils import make_temp_dir
from ...utils import ziptool

cli = CommandLineInterface()


class T:
    Manifest = T0.ManifestB
    Oss = Oss
    Path = T0.Path


@cli.cmd()
def install(appid: str) -> T.Path:
    """
    depsland install <url>
    """
    dir_i: T.Path  # the dir to last installed version (if exists)
    dir_m: T.Path = make_temp_dir()  # a temp dir to store downloaded assets
    dir_o: T.Path  # the dir to the new version
    
    oss = get_oss_client()
    oss_path = OssPath(appid)
    print(oss_path)
    
    # -------------------------------------------------------------------------
    
    def get_manifest_new() -> T.Manifest:
        nonlocal dir_m, oss, oss_path
        file_i = oss_path.manifest
        file_o = f'{dir_m}/manifest.pkl'
        oss.download(file_i, file_o)
        return loads(file_o)
    
    def get_manifest_old() -> T.Manifest:
        nonlocal dir_i, manifest_new
        dir_i = _get_dir_to_last_installed_version(appid)
        if dir_i:
            return load_manifest(f'{dir_i}/manifest.pkl')
        else:
            return init_manifest(manifest_new['appid'], manifest_new['name'])
    
    manifest_new = get_manifest_new()
    manifest_old = get_manifest_old()
    print(':l', manifest_new)
    
    # -------------------------------------------------------------------------
    
    def init_dir_o() -> T.Path:
        nonlocal manifest_new
        
        dir_o = '{}/{}/{}'.format(
            paths.project.apps,
            manifest_new['appid'],
            manifest_new['version']
        )
        if os.path.exists(dir_o):
            # FIXME: ask user turn to upgrade or reinstall command.
            raise FileExistsError(dir_o)
        
        paths_to_be_generated = sorted(set(
            fs.normpath(f'{dir_o}/{k}')
            for k, v in manifest['assets'].items()  # noqa
            if v.type == 'dir'
        ))
        print(':l', paths_to_be_generated)
        [os.makedirs(x, exist_ok=True) for x in paths_to_be_generated]
        
        manifest_new['start_directory'] = dir_o
        return dir_o
    
    dir_o = init_dir_o()
    
    # -------------------------------------------------------------------------
    
    _install_files(manifest_new, manifest_old, oss, oss_path, dir_m)
    _install_dependencies(manifest_new)
    
    if not config.debug_mode:
        fs.remove_tree(dir_m)
    fs.move(f'{dir_m}/manifest.pkl', f'{dir_o}/manifest.pkl', True)
    return dir_o


def _install_files(
        manifest_new: T.Manifest,
        manifest_old: T.Manifest,
        oss: T.Oss,
        oss_path: OssPath,
        temp_dir: T.Path
) -> None:
    root_0 = manifest_old['start_directory']
    root_1 = manifest_new['start_directory']
    for key_1, info_1 in manifest_new['assets'].items():
        if key_1 in manifest_old['assets']:
            key_o = key_1
            info_0 = manifest_old['assets'][key_o]
            if info_1.uid == info_0.uid:
                path_0 = f'{root_0}/{key_o}'
                path_1 = f'{root_1}/{key_1}'
                if info_1.type == 'dir':
                    fs.copy_tree(path_0, path_1)  # TODO: overwrite=True
                else:
                    fs.copy_file(path_0, path_1, True)
                continue
        
        # download from oss
        path_i = '{}/{}'.format(oss_path.assets, info_1.uid)  # an url
        path_m = fs.normpath('{}/{}{}'.format(  # an intermediate file (zip)
            temp_dir, key_1, '.zip' if info_1.type == 'dir' else '.fzip'
        ))
        path_o = '{}/{}'.format(root_1, key_1)  # final file or dir
        
        print('oss download', '{} -> {}'.format(path_i, path_m))
        oss.download(path_i, path_m)
        ziptool.unzip_file(path_m, path_o, overwrite=True)


def _install_dependencies(manifest: T.Manifest) -> None:
    packages = {}
    for name, vspec in manifest['dependencies'].items():  # noqa
        name = normalize_name(name)
        vspecs = tuple(normalize_version_spec(name, vspec))
        packages[name] = vspecs
    print(':vl', packages)
    
    name_ids = tuple(pypi.install(packages, include_dependencies=True))
    pypi.save_index()
    pypi.linking(name_ids, paths.apps.make_packages(
        manifest['appid'], clear_exists=True
    ))


# -----------------------------------------------------------------------------

def _get_dir_to_last_installed_version(appid: str) -> t.Optional[T.Path]:
    dir_ = '{}/{}'.format(paths.project.apps, appid)
    history_file = paths.apps.get_history_versions(appid)
    if os.path.exists(history_file):
        last_ver = loads(history_file)[0]
        out = f'{dir_}/{last_ver}'
        assert os.path.exists(out)
        return out
    return None
