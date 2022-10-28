import os
from argsense import CommandLineInterface
from lk_utils import fs
from lk_utils import loads
from ... import config
from ... import paths
from ...normalization import normalize_name
from ...normalization import normalize_version_spec
from ...oss import OssPath
from ...oss import get_oss_client
from ...oss.uploader import T as T0
from ...pypi import pypi
from ...utils import create_temporary_directory
from ...utils import ziptool

cli = CommandLineInterface()


class T:
    Manifest = T0.ManifestB
    Path = T0.Path


@cli.cmd()
def install(appid: str) -> T.Path:
    """
    depsland install <url>
    TODO: compare with old version, and download only different files.
    """
    dir_m: T.Path = create_temporary_directory()
    dir_o: T.Path
    
    oss = get_oss_client()
    oss_path = OssPath(appid)
    print(oss_path)
    
    # download manifest
    manifest_file = f'{dir_m}/manifest.pkl'
    oss.download(oss_path.manifest, manifest_file)
    manifest: T.Manifest = loads(manifest_file)
    # print(':v2', manifest['name'], manifest['version'])
    print(':l', manifest)
    
    # check dir_o
    dir_o = '{}/{}/{}'.format(
        paths.project.apps,
        manifest['appid'],
        manifest['version']
    )
    if os.path.exists(dir_o):
        # FIXME: ask user turn to upgrade or reinstall command.
        raise FileExistsError(dir_o)
    
    # assets (make dirs)
    paths_to_be_generated = sorted(set(
        fs.normpath(f'{dir_o}/{k}')
        for k, v in manifest['assets'].items()  # noqa
        if v.file_type == 'dir'
    ))
    print(':l', paths_to_be_generated)
    [os.makedirs(x, exist_ok=True) for x in paths_to_be_generated]
    
    # assets (download)
    for relpath, info in manifest['assets'].items():  # noqa
        link = '{}/{}'.format(oss_path.assets, info.key)
        zipped = fs.normpath('{}/{}{}'.format(
            dir_m, relpath,
            '.zip' if info.file_type == 'dir' else '.fzip'
        ))
        print('oss download', '{} -> {}'.format(link, zipped))
        oss.download(link, zipped)
        unzipped = fs.normpath('{}/{}'.format(dir_o, relpath))
        # print(':vl', zipped, unzipped)
        ziptool.unzip_file(zipped, unzipped, overwrite=True)
    
    # dependencies
    packages = {}
    for name, vspec in manifest['dependencies'].items():  # noqa
        name = normalize_name(name)
        vspecs = tuple(normalize_version_spec(name, vspec))
        packages[name] = vspecs
    print(':vl', packages)
    
    name_ids = tuple(pypi.install(packages, include_dependencies=True))
    pypi.save_index()
    pypi.linking(name_ids, paths.apps.make_packages(appid, clear_exists=True))
    
    if not config.debug_mode:
        fs.remove_tree(dir_m)
    fs.move(manifest_file, f'{dir_o}/manifest.pkl', True)
    return dir_o
