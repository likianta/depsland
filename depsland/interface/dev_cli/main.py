import os
from argsense import CommandLineInterface
from lk_utils import dumps
from lk_utils import fs
from ... import paths
from ...oss import upload as upload_assets
from ...profile_reader import T
from ...profile_reader import get_app_info

cli = CommandLineInterface('depsland.dev_cli')


@cli.cmd()
def init(directory: str = '.'):
    if directory != '.':
        if not os.path.exists(directory):
            os.mkdir(directory)
    if os.path.exists(x := f'{directory}/manifest.json'):
        r = input(f'target file ({x}) already exists, would you like to '
                  f'overwrite it? (y/n): ')
        if r == 'y':
            os.remove(x)
        else:
            print('[dim]no file creates[/]', ':r')
            return
    dirpath = fs.normpath(directory, force_abspath=True)
    dirname = fs.dirname(dirpath)
    manifest: T.Manifest = {
        'appid'       : dirname.replace(' ', '_').replace('-', '_').lower(),
        'name'        : dirname.replace('-', ' ').replace('_', ' ').title(),
        'version'     : '0.1.0',
        'assets'      : {},
        'dependencies': {},
    }
    dumps(manifest, x := f'{directory}/manifest.json')
    print(f'see manifest file at "{x}"')


@cli.cmd()
def upload(manifest_file: str = './manifest.json') -> None:
    appinfo = get_app_info(manifest_file)
    
    if not appinfo['history']:
        upload_assets(
            new_app_dir=appinfo['dst_dir'],
            old_app_dir=''
        )
    else:
        upload_assets(
            new_app_dir=appinfo['dst_dir'],
            old_app_dir='{}/{}/{}'.format(
                paths.Project.apps,
                appinfo['appid'],
                appinfo['history'][0]
            )
        )
    
    appinfo['history'].insert(0, appinfo['version'])
    dumps(appinfo['history'], '{}/{}/released_history.json'.format(
        paths.Project.apps, appinfo['appid'],
    ))


if __name__ == '__main__':
    cli.run()
