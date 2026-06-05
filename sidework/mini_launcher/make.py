import json
import sys

import neoprint as np
import tree_shaking
from argsense import cli
from lk_utils import fs
from lk_utils import run_cmd_args

fs.cd_current_dir()
depsland_project_root = '../..'


@cli
def init() -> None:
    fs.make_dir('dist')
    fs.make_link(f'{depsland_project_root}/python', 'dist/python')
    fs.make_link(
        'dist', f'{depsland_project_root}/resources/depsland-online-installer'
    )
    if not fs.exist('tree_shaking'):
        print(
            'suggest manually linking '
            '`<python_tree_shaking_project>/tree_shaking` here'
        )


@cli
def tree_shaking_depsland_online_installer(
    minify: bool = True, compress: bool = True, upload: bool = False
) -> None:
    """
    params:
        minify (-m):
        compress (-c):
        upload (-u):

    note: if you have upgraded some dependencies in
    `<depsland_project>/pyproject.toml`, also check this place
    `./pyproject.toml`.

    tip: if you have only modified "depsland_online_installer/main2.py", but not
    changed venv packages, you can rerun this command by
    `minify=False, compress=True` to fast refresh result.

    post check:
        - if the size of `<depsland_project>/resources/depsland-online-installer
            .zip` has notably changed, check some statements in
            `./app_launcher.v : download_and_extract_depsland_ol : println`.
    """
    if minify:
        tree_shaking.build_module_graphs(
            'depsland_online_installer/tree_shaking.yaml'
        )
        tree_shaking.dump_tree(
            'depsland_online_installer/tree_shaking.yaml', 'dist/minideps'
        )
    if compress:
        fs.copy_file('depsland_online_installer/main2.py', 'dist/main.py', True)
        result = fs.zip(
            f'{depsland_project_root}/resources/depsland-online-installer',
            f'{depsland_project_root}/resources/depsland-online-installer.zip',
            compression_level='maximum',
            overwrite=True,
            progress=True,
        )
        np.show(
            'see "<depsland_project>/resources/depsland-online-installer.zip" '
            '({}).'.format(fs.filesize(result, str))
        )
        if upload:
            run_cmd_args(
                (
                    'ossutil',
                    'cp',
                    '{}/resources/depsland-online-installer.zip'.format(
                        depsland_project_root
                    ),
                    'oss://likianta-public-share/depsland-resources/depsland'
                    '-online-installer.zip',
                    '-u',
                ),
                verbose=True,
            )
        else:
            np.show(
                'you may also want to upload this file to "<oss>/likianta'
                '-public-share/depsland-resources/depsland-online-installer'
                '.zip".'
            )


@cli
def create_launcher(
    target_name: str,
    target_appid,
    target_version,
    file_out: str,
    icon: str = '',
    show_console: bool = False,
    debug: bool = False,
) -> None:
    if fs.isdir(file_out):
        file_out += '/{}.exe'.format(target_name)
    else:
        assert file_out.endswith('.exe')

    fs.dump(
        {
            'appid': target_appid,
            'name': target_name,
            'version': target_version,
            'depsland_ol_url': (
                debug
                and 'http://172.20.128.100:2188/depsland-online-installer.zip'
                or 'https://likianta-public-share.oss-cn-shanghai.aliyuncs.com/'
                'depsland-resources/depsland-online-installer.zip'
            ),
        },
        '_target_meta.json',
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
    """
    params:
        file_out (-o):
    """
    sys.path.append(depsland_project_root)
    from depsland import load_manifest
    from depsland.api.dev_api import load_config

    conf = fs.load(profile)
    if 'images' in conf:
        conf2 = load_config(profile)
        for k in ('src_min', 'enc_max', 'enc_min', 'src_max'):
            if v := conf2['images'].get(k):
                assert isinstance(v, str)
                manifest = load_manifest(v)
                break
        else:
            raise Exception(conf2['images'])
    else:
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


# ------------------------------------------------------------------------------
# DELETE: nuitka related build functions are deprecated.


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
        True,
    )


@cli
def nuitka_build_general_launcher() -> None:
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
        """
        launchers built:
            {}: {}
            {}: {}
        """.format(
            'general_launcher_console.exe',
            fs.filesize('general_launcher/general_launcher_console.exe', str),
            'general_launcher_noconsole.exe',
            fs.filesize('general_launcher/general_launcher_noconsole.exe', str),
        ),
        ':t',
    )


@cli
def nuitka_create_launcher(
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
        show_console
        and 'general_launcher/general_launcher_console.exe'
        or 'general_launcher/general_launcher_noconsole.exe'
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
            w.write(
                raw
                + b'__DEPSLAND_CONFIG__'
                + json.dumps(
                    {
                        'appid': target_appid,
                        'name': target_name,
                        'version': target_version,
                        'show_console': show_console,
                    }
                ).encode('utf-8')
            )
    else:
        with open(base_exe, 'rb') as r, open(file_out, 'wb') as w:
            w.write(
                r.read()
                + b'__DEPSLAND_CONFIG__'
                + json.dumps(
                    {
                        'appid': target_appid,
                        'name': target_name,
                        'version': target_version,
                        'show_console': show_console,
                    }
                ).encode('utf-8')
            )

    print(':tv4', f'see "{file_out}" ({fs.filesize(file_out, str)})')


if __name__ == '__main__':
    # pox sidework/mini_launcher/make.py -h
    # pox sidework/mini_launcher/make.py tree_shaking_depsland_online_installer
    #   -m -c -u
    # pox sidework/mini_launcher/make.py tree_shaking_depsland_online_installer
    #   -M -c -u
    # pox sidework/mini_launcher/make.py create_launcher_from_profile ...
    cli.run()
