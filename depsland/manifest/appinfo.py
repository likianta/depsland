import typing as tp

from lk_utils import fs

from .manifest import dump_manifest
from .manifest import load_manifest
from .typing import T
from .. import paths


def get_app_info(manifest_file: str) -> T.Appinfo:
    """
    load origin manifest file, copy it to `<depsland>/apps` hosted directory -
    for unified management. and refresh the history file.
    """
    data_i: T.ManifestObject = load_manifest(manifest_file)
    data_o: T.Appinfo = {
        'appid': data_i['appid'],
        'name': data_i['name'],
        'version': data_i['version'],
        'src_dir': fs.dirpath(manifest_file),
        'dst_dir': '{}/{}/{}'.format(
            paths.project.apps, data_i['appid'], data_i['version']
        ),
        'history': [],
    }

    if not fs.exist(d := data_o['dst_dir']):
        fs.make_dirs(d)
    dump_manifest(data_i, f'{d}/manifest.json')

    # update history
    history_file = paths.apps.get_distribution_history(data_o['appid'])
    if fs.exist(history_file):
        data_o['history'] = fs.load(history_file, 'plain').splitlines()
    else:
        print(
            'no history found, it would be the first release',
            data_o['name'],
            data_o['version'],
            ':v2',
        )
        # dumps('', history_file, type='plain')

    return data_o


def get_last_installed_version(appid: str) -> tp.Optional[str]:
    file = paths.apps.get_installation_history(appid)
    if not fs.exist(file):
        return None
    return _quick_read_line(file)


def get_last_released_version(appid: str) -> tp.Optional[str]:
    file = paths.apps.get_distribution_history(appid)
    if not fs.exist(file):
        return None
    return _quick_read_line(file)


def _quick_read_line(text_file: str) -> str:
    with open(text_file, 'r', encoding='utf-8') as f:
        for line in f:  # just read the first line
            return line.strip()
        else:
            raise Exception
