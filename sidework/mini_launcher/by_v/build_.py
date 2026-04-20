"""
build the launcher.
why named "build_.py" not "build.py": avoid conflict with 
$[<site_packages>/build] package which is required by poetry executable.
"""
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

if __name__ == '__main__':
    cli.run()
