from os.path import exists

from lk_utils import fs

from ... import paths


def main(appid: str, version: str) -> None:
    for dir_ in (
            '{}/{}/{}'.format(paths.apps.root, appid, version),
            '{}/{}'.format(paths.apps.venv, appid),
    ):
        if exists(dir_):
            print('remove', dir_, ':i')
            fs.remove_tree(dir_)
    
    for file in (
            '{}/{}.exe'.format(paths.project.apps_launcher, appid),
            # '{}/{}.bat'.format(paths.project.apps_launcher, appid),
            # '{}/{}'.format(paths.project.apps_launcher, appid),
            # '{}/{}.exe'.format(paths.system.desktop, appid),
            # '{}/{}.exe'.format(paths.system.start_menu, appid),
    ):
        if exists(file):
            print('remove', file, ':i')
            fs.remove_file(file)
