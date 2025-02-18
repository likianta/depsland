"""
see DEVNOTE.md
"""
import os
import sys

from argsense import cli
from lk_utils import fs
from lk_utils import run_cmd_args


@cli.cmd()
def help_me_choose_python(
    platform: str = sys.platform, arch: str = 'amd64'
) -> None:
    """
    homepage: https://github.com/indygreg/python-build-standalone/releases
    
    params:
        platform: darwin | linux | win32
        arch: amd64 | arm64
    
    note: do not choose "msvc-static" or "linux-musl" version.
    """
    match platform:
        case 'darwin':
            if arch == 'amd64':
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'x86_64-apple-darwin-install_only.tar.gz'
                )
            else:
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'aarch64-apple-darwin-install_only.tar.gz'
                )
        case 'linux':
            if arch == 'amd64':
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'x86_64-unknown-linux-gnu-install_only.tar.gz'
                )
            else:
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'aarch64-unknown-linux-gnu-install_only.tar.gz'
                )
        case 'win32':
            if arch == 'amd64':
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'x86_64-pc-windows-msvc-install_only.tar.gz'
                )
            else:
                raise Exception(platform, arch)
        case _:
            raise Exception(platform, arch)
    print('please manually download python standalone from:')
    print('    ' + link)


@cli.cmd()
def init_pypi_blank(target_dir: str = 'chore/pypi_blank') -> None:
    """
    if you want to repair `chore/pypi_blank/index`, run this command.
    """
    fs.make_dir(f'{target_dir}')
    fs.make_dir(f'{target_dir}/cache')
    fs.make_dir(f'{target_dir}/downloads')
    fs.make_dir(f'{target_dir}/index')
    fs.make_dir(f'{target_dir}/index/snapdep')
    fs.make_dir(f'{target_dir}/installed')
    fs.dump({}, f'{target_dir}/index/id_2_paths.json')
    fs.dump({}, f'{target_dir}/index/name_2_vers.json')


@cli.cmd()
def make_site_packages(
    target_dir: str = 'chore/site_packages',
    remove_exists: bool = False
) -> None:
    """
    prerequisite:
        pox sidework/merge_external_venv_to_local_pypi.py .
    """
    from depsland import pypi
    from depsland.depsolver import resolve_dependencies
    
    if remove_exists and fs.exists(target_dir):
        fs.remove_tree(target_dir)
    if not fs.exists(target_dir):
        fs.make_dir(target_dir)
        fs.copy_file('chore/.gitkeep', f'{target_dir}/.gitkeep')
    
    pkgs = resolve_dependencies('poetry.lock', fs.xpath('..'))
    pkg_ids = (x['id'] for x in pkgs.values())
    pypi.linking(pkg_ids, target_dir)


@cli.cmd()
def make_minified_site_packages(
    tree_shaking_project_path: str = fs.xpath('../../python-tree-shaking')
) -> None:
    from depsland.utils import make_temp_dir
    
    os.environ.pop('VIRTUAL_ENV')
    
    run_cmd_args(
        ('poetry', 'run', 'python', '-m', 'tree_shaking'),
        (
            'build-module-graphs',
            fs.xpath('build_tool/_tree_shaking_model.yaml')
        ),
        cwd=tree_shaking_project_path,
        verbose=True,
        force_term_color=True,
    )
    
    run_cmd_args(
        ('poetry', 'run', 'python', '-m', 'tree_shaking'),
        (
            'dump-tree',
            fs.xpath('build_tool/_tree_shaking_model.yaml'),
            x := make_temp_dir()
        ),
        cwd=tree_shaking_project_path,
        verbose=True,
        force_term_color=True,
    )
    print(x, ':v')
    
    # postfix
    fs.remove(f'{x}/venv/numpy.libs')
    _make_empty_package(f'{x}/venv/matplotlib')
    _make_empty_package(f'{x}/venv/numpy')
    _make_empty_package(f'{x}/venv/pandas')
    
    fs.move(f'{x}/venv', 'chore/minified_site_packages', True)


def _make_empty_package(path) -> None:
    fs.remove(path)
    fs.make_dir(path)
    fs.dump('', f'{path}/__init__.py')


if __name__ == '__main__':
    # pox build/init.py help-me-choose-python
    # pox build/init.py make-site-packages --remove-exists
    # pox build/init.py make-minified-site-packages
    cli.run()
