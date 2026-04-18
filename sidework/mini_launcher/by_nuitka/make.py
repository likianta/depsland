import json
import sys
import tree_shaking
import typing as tp
from argsense import cli
from lk_utils import cd_current_dir, fs, run_cmd_args

cd_current_dir()
depsland_project_root = '../../..'

@cli
def init() -> None:
    fs.make_dir('dist')
    fs.make_link(f'{depsland_project_root}/python', 'dist/python')
    fs.make_link(
        'dist', f'{depsland_project_root}/resources/depsland_online_installer'
    )
    # fs.make_link('depsland_online_installer/main1.py', 'dist/main.py')

@cli
def tree_shaking_depsland_online_installer(
    do_minify: bool = True, do_compress: bool = True
) -> None:
    """
    params:
        do_minify (-m):
        do_compress (-c):

    tip: if you have only modified "depsland_online_installer/main.py", you can 
    rerun this command by `do_minify=False, do_compress=True` to fast refresh 
    result.
    """
    if do_minify:
        tree_shaking.build_module_graphs(
            'depsland_online_installer/tree_shaking.yaml'
        )
        tree_shaking.dump_tree(
            'depsland_online_installer/tree_shaking.yaml',
            'dist/minideps'
        )
    if do_compress:
        fs.copy_file(
            'depsland_online_installer/main2.py',
            'dist/main.py',
            True
        )
        result = fs.zip(
            f'{depsland_project_root}/resources/depsland_online_installer', 
            f'{depsland_project_root}/resources/depsland_online_installer.zip',
            overwrite=True,
            progress=True,
        )
        print(fs.filesize(result, str))

@cli
def nuitka_compile_depsland_online_installer() -> None:
    # warning: this is time consuming.
    # the output exe file size is ~17mb.
    run_cmd_args(
        sys.executable,
        '-m',
        'nuitka',
        '--onefile',
        '--standalone',
        '--windows-console-mode=force',
        '--noinclude-IPython-mode=nofollow',
        '--output-filename=depsland_online_installer.exe',
        'main2.py',
        verbose=True,
        cwd='depsland_online_installer',
    )
    fs.copy_file(
        'depsland_online_installer/depsland_online_installer.exe',
        f'{depsland_project_root}/resources/depsland_online_installer.exe',
        True
    )

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
        cwd='general_launcher',
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
        cwd='general_launcher',
    )
    print(
        '''
        launchers built:
            {}: {}
            {}: {}
        '''.format(
            'general_launcher_console.exe',
            fs.filesize('general_launcher/general_launcher_console.exe', str),
            'general_launcher_noconsole.exe',
            fs.filesize('general_launcher/general_launcher_noconsole.exe', str),
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
        'general_launcher/general_launcher_console.exe' or
        'general_launcher/general_launcher_noconsole.exe'
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
        sys.path.append(depsland_project_root)
        from depsland.platform.launcher.make_exe import add_icon_to_exe

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

@cli
def create_launcher_from_manifest(
    mainfest_file: str,
    dir_out: str = '',
    file_out: str = '',
    show_console: tp.Optional[bool] = None,
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
    cli.run()
