from argsense import CommandLineInterface
from lk_utils import dumps
from ... import paths
from ...profile_reader import get_app_info
from ...oss import upload as upload_assets

cli = CommandLineInterface('depsland.dev_cli')


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
                paths.apps_dir,
                appinfo['appid'],
                appinfo['history'][0]
            )
        )
    
    appinfo['history'].insert(0, appinfo['version'])
    dumps(appinfo['history'], '{}/{}/released_history.json'.format(
        paths.apps_dir, appinfo['appid'],
    ))


if __name__ == '__main__':
    cli.run()
