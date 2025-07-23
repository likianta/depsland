import sys
from argsense import cli
from lk_utils import fs
from lk_utils import run_cmd_args


@cli
def main(
    target_appid,
    target_version,
    file_out: str,
    icon: str = None,
    show_console: bool = False,
    **kwargs
) -> None:
    """
    params:
        **kwargs:
            console_mode: force | disable | attach | hide
                force: always show console.
                disable: never show console.
                attach (default):
                    double click run = hide console;
                    terminal run = show console
                hide:
                    same like "attach", but use a different method to hide a -
                    console.
                FIXME:
                    currently found that "attach" behaves like "disable", -
                    while "hide" behaves like "force".
    """
    code_temp: str = fs.load(fs.xpath('_template.py'), 'plain')
    code_out = (
        code_temp
        .replace('<APPID>', target_appid)
        .replace('<VERSION>', target_version)
    )
    
    temp_py = fs.xpath('temp/run_{}.py'.format(target_appid))
    temp_exe = fs.xpath('temp/run_{}.exe'.format(target_appid))
    fs.dump(code_out, temp_py, 'plain')
    run_cmd_args(
        sys.executable,
        '-m',
        'nuitka',
        '--standalone',
        '--onefile',
        '--windows-console-mode={}'.format(
            # 'force' if show_console else 'attach'
            'force' if show_console else kwargs.get('console_mode', 'attach')
        ),
        icon and '--windows-icon-from-ico={}'.format(icon),
        fs.basename(temp_py),
        verbose=True,
        cwd=fs.xpath('temp'),
    )
    # if icon:
    #     sys.path.append(fs.xpath('../../..'))
    #     from depsland.platform.launcher.make_exe import add_icon_to_exe
    #     add_icon_to_exe(temp_path, icon)
    fs.copy_file(temp_exe, file_out, True)
    print(':tv4', 'done. see "{}"'.format(file_out.replace('\\', '/')))


@cli
def manifest(
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
    if file_out is None:
        if dir_out is None:
            dir_out = '{}/dist'.format(mani['start_directory'])
        if debug:
            name_template = '{} v{} (Debug).exe'
        else:
            name_template = '{} v{}.exe'
        name = name_template.format(mani['name'], mani['version'])
        file_out = '{}/{}'.format(dir_out, name)
    
    main(
        target_appid=mani['appid'],
        target_version=mani['version'],
        file_out=file_out,
        icon=mani['launcher']['icon'],
        show_console=show_console,
    )


if __name__ == '__main__':
    # pox sidework/mini_launcher/by_nuitka/factory.py -h
    # pox sidework/mini_launcher/by_nuitka/factory.py manifest -h
    cli.run()
