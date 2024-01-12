from lk_utils import fs

from ... import paths


def main(appid: str, version: str, **kwargs) -> None:
    try:
        fs.remove_tree('{}/{}/{}'.format(
            paths.apps.root, appid, version
        ))
        
        if kwargs.get('remove_venv', True):
            fs.remove_tree('{}/{}'.format(
                paths.apps.venv, appid
            ))
        
        if kwargs.get('remove_bin', True):
            fs.remove_file('{}/{}.exe'.format(
                paths.apps.bin, appid
            ))
    except PermissionError:  # TODO
        print(
            'failed to remove old version, '
            'we will try to delete it again next time', ':v4'
        )
