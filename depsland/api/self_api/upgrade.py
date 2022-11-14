import os
import typing as t

from lk_utils import fs

from ... import paths
from ...manifest import T as T0
from ...manifest import change_start_directory
from ...manifest import init_target_tree
from ...manifest import load_manifest
from ...oss import T as T1
from ...oss import get_oss_client
from ...utils import compare_version
from ...utils import make_temp_dir


class T:
    Manifest = T0.Manifest
    Oss = T1.Oss
    CheckUpdatesResult = t.Optional[t.Tuple[Manifest, Manifest]]


_is_dev_mode = False


def main() -> None:
    oss = get_oss_client(appid='depsland')
    
    if not (x := _get_manifests(oss)):
        print('no update available')
        return
    else:
        manifest0: T.Manifest
        manifest1: T.Manifest
        manifest0, manifest1 = x
    
    dir0, dir1 = _init_directories(manifest0, manifest1)
    temp_dir = make_temp_dir()
    
    global _is_dev_mode
    _is_dev_mode = os.path.islink(paths.project.python)
    
    _install_files(manifest1, manifest0, oss, temp_dir)
    _install_custom_packages(manifest1, manifest0, oss)
    _install_dependencies(manifest1, dst_dir=paths.python.site_packages)
    
    # overwrite files from dir1 to dir0
    for name in os.listdir(dir1):
        if name in ('apps', 'pypi', 'python', 'temp'):
            continue
        print(':i', name)
        fs.move(f'{dir1}/{name}', f'{dir0}/{name}', overwrite=True)
    
    fs.move(
        f'{paths.temp.self_upgrade}/manifest.pkl',
        f'{dir0}/manifest.pkl',
        True
    )


def _get_manifests(oss) -> T.CheckUpdatesResult:
    oss.download(
        oss.path.manifest,
        latest_manifest_file := f'{paths.temp.self_upgrade}/manifest.pkl'
    )
    
    manifest0 = load_manifest(paths.project.manifest_pkl)
    manifest1 = load_manifest(latest_manifest_file)
    print(':v', manifest0['version'], manifest1['version'])
    
    if compare_version(manifest0['version'], '<', manifest1['version']):
        return manifest0, manifest1
    else:
        return None


def _init_directories(
        manifest0: T.Manifest, manifest1: T.Manifest
) -> t.Tuple[str, str]:
    dir0 = paths.system.depsland
    dir1 = paths.temp.self_upgrade + '/' + manifest1['version']
    assert dir0 is not None
    init_target_tree(manifest1, dir1)  # complete tree of `dir1`
    change_start_directory(manifest0, dir0)
    change_start_directory(manifest1, dir1)
    return dir0, dir1


def _install_files(
        manifest1: T.Manifest,
        manifest0: T.Manifest,
        oss: T.Oss,
        temp_dir: str
) -> None:
    from ..user_api.install import _install_files  # noqa
    _install_files(manifest1, manifest0, oss, temp_dir)


def _install_custom_packages(
        manifest1: T.Manifest,
        manifest0: T.Manifest,
        oss: T.Oss
) -> None:
    if _is_dev_mode:
        return
    from ..user_api.install import _install_custom_packages  # noqa
    _install_custom_packages(manifest1, manifest0, oss)


def _install_dependencies(manifest1: T.Manifest, dst_dir: str) -> None:
    if _is_dev_mode:
        return
    from ...pip import pip
    for name, vspec in manifest1['dependencies'].items():
        pip.install(name, vspec, dst_dir=dst_dir)
