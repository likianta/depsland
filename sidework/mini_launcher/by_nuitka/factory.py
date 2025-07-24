import sys
from argsense import cli
from depsland.platform.launcher.make_exe import add_icon_to_exe
from lk_utils import fs
from lk_utils import run_cmd_args


@cli.cmd('main')
def create_launcher(
    target_appid,
    target_version,
    file_out: str,
    icon: str = None,
    show_console: bool = False,
    **kwargs
) -> None:
    """
    params:
        icon (-i):
        show_console (-c):
        **kwargs:
            console_mode: force | disable | attach | hide
                force: always show console.
                disable (default): never show console.
                attach:
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
    
    temp_py = fs.xpath('temp/run_{}.py'.format(
        'common' if target_appid == '<FROM_FILENAME>' else target_appid
    ))
    temp_exe = fs.xpath('temp/run_{}.exe'.format(
        'common' if target_appid == '<FROM_FILENAME>' else target_appid
    ))
    fs.dump(code_out, temp_py, 'plain')
    run_cmd_args(
        sys.executable,
        '-m',
        'nuitka',
        '--standalone',
        '--onefile',
        '--windows-console-mode={}'.format(
            # 'force' if show_console else 'attach'
            'force' if show_console else kwargs.get('console_mode', 'disable')
        ),
        icon and '--windows-icon-from-ico={}'.format(fs.abspath(icon)),
        fs.basename(temp_py),
        verbose=True,
        cwd=fs.xpath('temp'),
    )
    # if icon:
    #     add_icon_to_exe(temp_path, icon)
    fs.copy_file(temp_exe, file_out, True)
    if kwargs.get('_verbose', True):
        print(':tv4', 'done. see "{}"'.format(file_out.replace('\\', '/')))


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
        target_appid=mani['appid'],
        target_version=mani['version'],
        file_out=file_out,
        icon=mani['launcher']['icon'],
        show_console=show_console,
    )


@cli.cmd('common')
def create_common_launcher(
    target_appid,
    target_version,
    dir_out: str,
    icon: str = None,
    show_console: bool = False,
) -> None:
    if not fs.exist(common1 := 'build/exe/mini-launcher-common.exe'):
        create_launcher(
            target_appid='<FROM_FILENAME>',
            target_version='<FROM_FILENAME>',
            file_out=common1,
            icon='build/icon/python.ico',
            show_console=False,
            _verbose=False
        )
    if not fs.exist(common2 := 'build/exe/mini-launcher-common-debug.exe'):
        create_launcher(
            target_appid='<FROM_FILENAME>',
            target_version='<FROM_FILENAME>',
            file_out=common2,
            icon='build/icon/python.ico',
            show_console=True,
            _verbose=False
        )
    
    file_out = '{}/{}-v{}-{}.exe'.format(
        dir_out,
        target_appid,
        target_version,
        'debug' if show_console else 'common'
    )
    fs.copy_file(common2 if show_console else common1, file_out, True)
    if icon:
        add_icon_to_exe(file_out, icon)
    print(':tv4', 'done. see "{}"'.format(file_out.replace('\\', '/')))


if __name__ == '__main__':
    # pox sidework/mini_launcher/by_nuitka/factory.py -h
    # pox sidework/mini_launcher/by_nuitka/factory.py manifest -h
    cli.run()
