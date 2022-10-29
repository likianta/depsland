import os
import re
from argsense import CommandLineInterface
from lk_utils import dumps, loads
from lk_utils import fs
from os.path import exists
from ... import paths
from ...manifest import T
from ...manifest import get_app_info
from ...oss import upload as upload_assets

cli = CommandLineInterface('depsland.dev_cli')


@cli.cmd()
def init(directory: str = '.', overwrite=False, auto_find_requirements=False):
    """
    kwargs:
        auto_find_requirements (-a):
        overwrite (-o):
    """
    if directory != '.':
        if not exists(directory):
            os.mkdir(directory)
    if exists(x := f'{directory}/manifest.json'):
        if overwrite:
            os.remove(x)
        else:
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
    
    if auto_find_requirements:
        if exists(x := f'{dirpath}/requirements.txt'):
            pattern = re.compile(r'([-\w]+)(.*)')
            deps = manifest['dependencies']
            for line in loads(x).splitlines():  # type: str
                if line and not line.startswith('#'):
                    name, ver = pattern.search(line).groups()
                    deps[name] = ver.replace(' ', '')
            print(deps, ':l')
    
    dumps(manifest, x := f'{dirpath}/manifest.json')
    print(f'see manifest file at "{x}"')


@cli.cmd()
def upload(manifest_file: str = './manifest.json') -> None:
    appinfo = get_app_info(manifest_file)
    
    if not appinfo['history']:
        upload_assets(
            new_app_dir=appinfo['src_dir'],
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
