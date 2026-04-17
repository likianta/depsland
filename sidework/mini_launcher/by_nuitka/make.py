import sys
import tree_shaking
from argsense import cli
from lk_utils import cd_current_dir, fs, run_cmd_args

cd_current_dir()
depsland_project_root = '../../..'

@cli
def init():
    fs.make_dir('dist')
    # fs.make_link('depsland_online_installer/main.py', 'dist/main.py')

@cli
def tree_shaking_depsland_online_installer(
    do_minify: bool = True, do_compress: bool = True
):
    """
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
            'depsland_online_installer/main1.py',
            'dist/main.py',
            True,
        )
        result = fs.zip(
            'dist', 
            '{}/resources/depsland_online_installer.zip'
            .format(depsland_project_root),
            True,
        )
        print(fs.filesize(result, str))

@cli
def nuitka_compile_depsland_online_installer():
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

if __name__ == '__main__':
    cli.run()
