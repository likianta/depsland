"""
see DEVNOTE.md
"""
import sys

from argsense import cli

from lk_utils import fs

from depsland import pypi
from depsland.depsolver import resolve_dependencies


@cli.cmd()
def help_me_choose_python(
    platform: str = sys.platform,
    arch: str = 'x86_64',  # 'aarch64', 'x86_64'
) -> None:
    """
    homepage: https://github.com/indygreg/python-build-standalone/releases
    note: do not choose "msvc-static" or "linux-musl" version.
    """
    match platform:
        case 'darwin':
            if arch == 'aarch64':
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'aarch64-apple-darwin-install_only.tar.gz'
                )
            else:
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'x86_64-apple-darwin-install_only.tar.gz'
                )
        case 'linux':
            if arch == 'aarch64':
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'aarch64-unknown-linux-gnu-install_only.tar.gz'
                )
            else:
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'x86_64-unknown-linux-gnu-install_only.tar.gz'
                )
        case 'win32':
            if arch == 'aarch64':
                raise Exception(platform, arch)
            else:
                link = (
                    'https://github.com/indygreg/python-build-standalone/'
                    'releases/download/20240415/cpython-3.12.3+20240415-'
                    'x86_64-pc-windows-msvc-install_only.tar.gz'
                )
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
    if remove_exists and fs.exists(target_dir):
        fs.remove_tree(target_dir)
    if not fs.exists(target_dir):
        fs.make_dir(target_dir)
        fs.copy_file('chore/.gitkeep', f'{target_dir}/.gitkeep')
    
    pkgs = resolve_dependencies('poetry.lock', fs.xpath('..'))
    pkg_ids = (x['id'] for x in pkgs.values())
    pypi.linking(pkg_ids, target_dir)


@cli.cmd()
def make_minified_site_packages(dir_i: str) -> None:
    dir_o = 'chore/minified_site_packages'
    fs.remove(dir_o)
    fs.make_link(dir_i, dir_o)
    fs.copy_file('chore/.gitkeep', f'{dir_o}/.gitkeep')


if __name__ == '__main__':
    # pox build/init.py help-me-choose-python
    # pox build/init.py make-site-packages --remove-exists
    # pox build/init.py make-minified-site-packages <dir_i>
    cli.run()
