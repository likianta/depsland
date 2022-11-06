import typing as t

from ... import paths
from ...manifest import load_manifest
from ...manifest import T as T0
from ...oss import OssPath
from ...oss import get_oss_client
from ...utils import compare_version

_oss = get_oss_client()


class T:
    Manifest = T0.Manifest
    CheckUpdatesResult = t.Optional[t.Tuple[Manifest, Manifest]]


def main() -> None:
    if not (x := _check_updates()):
        print('no updates available.')
        return
    else:
        manifest0, manifest1 = x
    

def _check_updates() -> T.CheckUpdatesResult:
    """
    return True if there is an update available.
    """
    oss_path = OssPath(appid='depsland')
    _oss.download(
        oss_path.manifest,
        latest_manifest_file := f'{paths.temp.self_update}/manifest.pkl'
    )
    
    manifest0 = load_manifest(paths.conf.manifest)
    manifest1 = load_manifest(latest_manifest_file)
    
    if compare_version(manifest0['version'], '<', manifest1['version']):
        return manifest0, manifest1
    else:
        return None
