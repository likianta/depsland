import os
import typing as t

from lk_utils import fs

from ..user_api.install import _install_custom_packages  # noqa
from ..user_api.install import _install_dependencies  # noqa
from ..user_api.install import _install_files  # noqa
from ... import paths
from ...manifest import T as T0
from ...manifest import init_target_tree
from ...manifest import load_manifest
from ...oss import OssPath
from ...oss import get_oss_client
from ...utils import compare_version
from ...utils import make_temp_dir


class T:
    Manifest = T0.Manifest
    CheckUpdatesResult = t.Optional[t.Tuple[Manifest, Manifest]]


def main() -> None:
    oss = get_oss_client()
    oss_path = OssPath(appid='depsland')
    
    if not (x := _get_manifests(oss, oss_path)):
        print('no updates available.')
        return
    else:
        manifest0: T.Manifest
        manifest1: T.Manifest
        manifest0, manifest1 = x
    
    dir0 = paths.system.depsland_bak
    dir1 = paths.system.depsland
    _init_directories(manifest0, manifest1, dir0, dir1)
    
    temp_dir = make_temp_dir(root=f'{dir0}/temp')
    
    _install_files(manifest1, manifest0, oss, oss_path, temp_dir)
    _install_custom_packages(manifest1, manifest0, oss, oss_path)
    _install_dependencies(manifest1, dst_dir=paths.python.site_packages)
    
    fs.remove_tree(dir0)


def _get_manifests(oss, oss_path) -> T.CheckUpdatesResult:
    oss.download(
        oss_path.manifest,
        latest_manifest_file := f'{paths.temp.self_upgrade}/manifest.pkl'
    )
    
    manifest0 = load_manifest(paths.conf.manifest)
    manifest1 = load_manifest(latest_manifest_file)
    
    if compare_version(manifest0['version'], '<', manifest1['version']):
        return manifest0, manifest1
    else:
        return None


def _init_directories(
        manifest0: T.Manifest, manifest1: T.Manifest,
        dir0: str, dir1: str,
) -> None:
    fs.move(dir1, dir0, True)  # backup
    fs.move(f'{dir0}/apps', f'{dir1}/apps', True)
    fs.move(f'{dir0}/apps_launcher', f'{dir1}/apps_launcher', True)
    fs.move(f'{dir0}/pypi', f'{dir1}/pypi', True)
    fs.move(f'{dir0}/python', f'{dir1}/python', True)
    fs.move(f'{dir1}/python/Lib/site-packages',
            f'{dir0}/python-lib-site_packages', True)
    os.mkdir(f'{dir1}/python/Lib/site-packages')
    init_target_tree(manifest1, dir1)  # init tree of `dir1`
    
    manifest0['start_directory'] = dir0
    manifest1['start_directory'] = dir1
