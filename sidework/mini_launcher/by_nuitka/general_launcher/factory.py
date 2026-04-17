# if __name__ == '__main__':
#     import sys
#     from lk_utils import cd_current_dir
#     cd_current_dir()
#     sys.path.append('../../../')  # path to find `depsland`
#     sys.path.append('../../../lib')  # path to find `tree_shaking`

import json
import sys
from argsense import cli
from depsland.platform.launcher.make_exe import add_icon_to_exe
from lk_utils import cd_current_dir
from lk_utils import fs
from lk_utils import run_cmd_args

cd_current_dir()

@cli
def build_general_launcher() -> None:
    """
    https://chatgpt.com/share/69ddb859-0b78-8321-8407-fc3b8a7d8976
    """
    run_cmd_args(
        sys.executable,
        '-m',
        'nuitka',
        '--onefile',
        '--standalone',
        '--windows-console-mode=force',
        '--output-filename=general_launcher_console.exe',
        'template.py',
        verbose=True,
    )
    run_cmd_args(
        sys.executable,
        '-m',
        'nuitka',
        '--onefile',
        '--standalone',
        '--windows-console-mode=disable',
        '--output-filename=general_launcher_noconsole.exe',
        'template.py',
        verbose=True,
    )
    print(
        '''
        launchers built:
            {}: {}
            {}: {}
        '''.format(
            'general_launcher_console.exe',
            fs.filesize('general_launcher_console.exe', str),
            'general_launcher_noconsole.exe',
            fs.filesize('general_launcher_noconsole.exe', str),
        ),
        ':t'
    )

@cli
def create_launcher(
    target_name: str,
    target_appid,
    target_version,
    file_out: str = '',
    icon: str = '',
    show_console: bool = False,
) -> None:
    """
    params:
        file_out (-o): give a file path or directory.
            if file path is given, will overwrite it.
            if directory path is given, will create `<dir>/<target_name>.exe`.
            if not set, will create -
            `<this_dir>/generated_launchers/<target_name>.exe`.
        icon (-i):
        show_console (-c):
    """
    if file_out:
        if fs.isdir(file_out):
            file_out += '/{}.exe'.format(target_name)
    else:
        file_out = 'generated_launchers/{}.exe'.format(target_name)
    
    base_exe = (
        show_console and
        'general_launcher_console.exe' or
        'general_launcher_noconsole.exe'
    )

    # with (open(base_exe, 'rb') as r, open(file_out, 'wb') as w):
    #     w.write(r.read() + b'__DEPSLAND_CONFIG__' + json.dumps(
    #         {
    #             'appid': target_appid,
    #             'name': target_name,
    #             'version': target_version,
    #             'show_console': show_console,
    #         }
    #     ).encode('utf-8'))
    # print(b'__DEPSLAND_CONFIG__' in fs.load(file_out, 'binary'), ':v')
    # if icon:
    #     add_icon_to_exe(file_out, icon)
    #     print(b'__DEPSLAND_CONFIG__' in fs.load(file_out, 'binary'), ':v')

    if icon:
        fs.copy_file(base_exe, file_out, True)
        add_icon_to_exe(file_out, icon)
        
        with open(file_out, 'rb') as r:
            raw = r.read()
        with open(file_out, 'wb') as w:
            w.write(raw + b'__DEPSLAND_CONFIG__' + json.dumps(
                {
                    'appid'       : target_appid,
                    'name'        : target_name,
                    'version'     : target_version,
                    'show_console': show_console,
                }
            ).encode('utf-8'))
    else:
        with (open(base_exe, 'rb') as r, open(file_out, 'wb') as w):
            w.write(r.read() + b'__DEPSLAND_CONFIG__' + json.dumps(
                {
                    'appid'       : target_appid,
                    'name'        : target_name,
                    'version'     : target_version,
                    'show_console': show_console,
                }
            ).encode('utf-8'))
    
    print(':tv4', f'see "{file_out}" ({fs.filesize(file_out, str)})')

@cli.cmd('manifest')
def create_launcher_from_manifest(
    mainfest_file: str,
    dir_out: str = None,
    file_out: str = None,
    show_console: bool = None
) -> None:
    """
    params:
        dir_out (-d):
        file_out (-f):
        show_console (-c):
    """
    from depsland.manifest import load_manifest
    mani = load_manifest(mainfest_file)
    
    debug = bool(show_console)
    if show_console is None:
        show_console = mani['launcher']['show_console']
        print(':v', show_console)
    if file_out is None:
        if dir_out is None:
            dir_out = '{}/dist'.format(mani['start_directory'])
        if debug:
            name_template = '{} v{} (Debug).exe'
        else:
            name_template = '{} v{}.exe'
        name = name_template.format(mani['name'], mani['version'])
        file_out = '{}/{}'.format(dir_out, name)
    
    create_launcher(
        target_name=mani['name'],
        target_appid=mani['appid'],
        target_version=mani['version'],
        file_out=file_out,
        icon=mani['launcher']['icon'],
        show_console=show_console,
    )

if __name__ == '__main__':
    # pox sidework/mini_launcher/by_nuitka/general_launcher/factory.py -h
    # pox sidework/mini_launcher/by_nuitka/general_launcher/factory.py 
    #   build_general_launcher
    # pox sidework/mini_launcher/by_nuitka/general_launcher/factory.py 
    #   create_launcher ...
    # pox sidework/mini_launcher/by_nuitka/general_launcher/factory.py 
    #   create_launcher_from_manifest ...
    cli.run()
