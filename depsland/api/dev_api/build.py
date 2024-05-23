from lk_utils import fs

from ...manifest import load_manifest
from ...platform import create_launcher


def build(manifest_file: str) -> None:
    """
    what does this function do:
        - create a dist folder
        - create a launcher (.exe or .sh)
    """
    manifest = load_manifest(manifest_file)
    
    dir_i = manifest['start_directory']
    dir_o = '{}/dist/{}-{}'.format(
        dir_i, manifest['appid'], manifest['version']
    )
    fs.make_dirs(dir_o)
    
    # FIXME
    create_launcher(manifest, dir_o=dir_o)
    
    print(
        ':t',
        'build done. see result in "dist/{}-{}"'.format(
            manifest['appid'], manifest['version']
        )
    )
