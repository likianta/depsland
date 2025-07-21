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
) -> None:
    code_temp: str = fs.load(fs.xpath('_template.txt'), 'plain')
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
    print(':t', 'done. see {}'.format(file_out))


if __name__ == '__main__':
    cli.run(main)
