"""
see DEVNOTE.md
"""
import sys

from argsense import cli
from lk_utils import fs


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
    # noinspection PyUnreachableCode
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


def _make_empty_package(path) -> None:
    fs.remove(path)
    fs.make_dir(path)
    fs.dump('', f'{path}/__init__.py')


if __name__ == '__main__':
    # pox build/init.py help-me-choose-python
    cli.run()
