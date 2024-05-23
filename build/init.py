"""
see DEVNOTE.md
"""
import os
import sys

from argsense import cli
from lk_utils import fs
from lk_utils import run_cmd_args

os.chdir(fs.xpath('..'))
if not os.getenv('DEPSLAND_PYPI_ROOT'):
    os.environ['DEPSLAND_PYPI_ROOT'] = 'chore/pypi_self'

from depsland import paths
from depsland.pypi.insight import rebuild_index


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
def download_requirements() -> None:
    """
    prerequisite:
        - `python/python.exe` or `python/bin/python3`. if not exist, see
          `python/README.zh.md`.
    """
    run_cmd_args(
        paths.python.python, '-m', 'pip', 'wheel',
        '-r', 'requirements.lock',
        '--wheel-dir', 'chore/pypi_self/downloads',
        '--no-deps', '--disable-pip-version-check',
        verbose=True
    )


@cli.cmd()
def rebuild_pypi_index(perform_pip_install: bool = True) -> None:
    """
    trick: if you want to rebuild `pypi` instead of `chore/pypi_self`, set -
    environment variable `DEPSLAND_PYPI_ROOT` to `pypi` before running this -
    command. (remember to unset it after running)
    """
    assert paths.pypi.root.endswith(('/chore/pypi_self', '/pypi'))
    rebuild_index(perform_pip_install=perform_pip_install)


@cli.cmd()
def init_pypi_blank(target_dir: str = 'chore/pypi_blank') -> None:
    """
    if you want to repair `chore/pypi_blank/index`, run this command.
    """
    # fs.make_dir(f'{target_dir}')
    # fs.make_dir(f'{target_dir}/cache')
    # fs.make_dir(f'{target_dir}/downloads')
    # fs.make_dir(f'{target_dir}/index')
    # fs.make_dir(f'{target_dir}/index/snapdep')
    # fs.make_dir(f'{target_dir}/installed')
    fs.dump({}, f'{target_dir}/index/id_2_paths.json')
    fs.dump({}, f'{target_dir}/index/name_2_vers.json')


@cli.cmd()
def make_site_packages(
    target_dir: str = 'chore/site_packages',
    remove_exists: bool = False
) -> None:
    # run_cmd_args(
    #     paths.python.python, '-m', 'pip', 'install',
    #     '-r', 'requirements.lock',
    #     '-t', target_dir,
    #     '--find-links', 'chore/pypi_self/downloads',
    #     '--no-deps', '--no-index',
    #     '--no-warn-script-location', '--disable-pip-version-check',
    #     verbose=True
    # )
    
    import re
    from depsland import pypi
    from depsland.normalization import normalize_name
    from depsland.normalization import split_filename_of_package
    
    if remove_exists and fs.exists(target_dir):
        fs.remove_tree(target_dir)
    if not fs.exists(target_dir):
        fs.make_dir(target_dir)
        fs.copy_file('chore/.gitkeep', f'{target_dir}/.gitkeep')
    
    downloaded_packages = set()
    for f in fs.find_files('chore/pypi_self/downloads'):
        name, ver = split_filename_of_package(f.name)
        downloaded_packages.add(f'{name}-{ver}')
    
    valid_packages = []
    pattern = re.compile(r'([-\w]+)(?:\[.*?])?==([^ ]+)')
    for i, line in enumerate(fs.load('requirements.lock').splitlines(), 1):
        print(i, line, ':v')
        if not line or line.startswith(('#', '--')):
            continue
        if '@' in line:
            name, ver, _ = line.rsplit('/', 1)[1].split('-', 2)
        else:
            name, ver = pattern.search(line).groups()
        name = normalize_name(name)
        if (x := f'{name}-{ver}') in downloaded_packages:
            valid_packages.append(x)
        else:
            print(f'drop line {i}', line)
    
    pypi.linking(valid_packages, target_dir)


if __name__ == '__main__':
    # pox build/init.py help-me-choose-python
    # pox build/init.py download-requirements
    # pox build/init.py rebuild-pypi-index
    # pox build/init.py make-site-packages
    # pox build/init.py make-site-packages --remove-exists
    cli.run()
