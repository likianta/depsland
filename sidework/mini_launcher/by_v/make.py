import sys
from argsense import cli
from lk_utils import fs, run_cmd_args

fs.cd_current_dir()
depsland_project_root = '../../..'

@cli
def create_launcher(
    target_name: str,
    target_appid,
    target_version,
    file_out: str = '',
    icon: str = '',
    show_console: bool = False,
    debug: bool = False,
) -> None:
    if file_out:
        if fs.isdir(file_out):
            file_out += '/{}.exe'.format(target_name)
    else:
        file_out = 'generated_launchers/{}.exe'.format(target_name)
    
    fs.dump(
        {
            'appid': target_appid,
            'name': target_name,
            'version': target_version,
            'depsland_ol_url': (
                debug and 
                'http://172.20.128.100:2188/depsland-online-installer.zip' or 
                'https://likianta-public-share.oss-cn-shanghai.aliyuncs.com/'
                'depsland-resources/depsland-online-installer.zip'
            ),
        },
        'target.json',
    )
    run_cmd_args(('v', 'app_launcher.v'))
    print(fs.filesize('app_launcher.exe', str))

    fs.copy_file('app_launcher.exe', file_out, True)

    if icon:
        sys.path.append(depsland_project_root)
        from depsland.platform.launcher.make_exe import add_icon_to_exe
        add_icon_to_exe(file_out, icon)
    
    # TODO
    if not show_console:
        print(':v6', 'hiding console is work-in-progress')

@cli
def create_launcher_from_profile(profile: str, file_out: str = '') -> None:
    sys.path.append(depsland_project_root)
    from depsland import load_manifest
    manifest = load_manifest(profile)

    if file_out:
        if fs.isdir(file_out):
            file_out += '/{} v{}.exe'.format(
                manifest['name'], manifest['version']
            )
        else:
            assert file_out.endswith('.exe')
    else:
        file_out = '{}/dist/{} v{}.exe'.format(
            manifest['start_directory'], manifest['name'], manifest['version']
        )

    create_launcher(
        manifest['name'],
        manifest['appid'],
        manifest['version'],
        file_out,
        icon=manifest['launcher']['icon'],
        show_console=manifest['launcher']['show_console'],
    )
    print('see result at "{}"'.format(file_out), ':v4')

if __name__ == '__main__':
    cli.run()
