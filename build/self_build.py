"""
init `[prj]:/pypi` or `[prj]:/pypi_self` folder.
1. before run this script, make sure you have backed up the target folder \
    (`[prj]:/pypi` or `[prj]:/pypi_self`).
2. manually delete everything except ".gitkeep" in `<target_folder>/index/*`.
3. run this script:
    # get help
    pox build/self_build.py -h
    pox build/self_build.py init -h
    
    # init `[prj]:/pypi` folder
    pox build/self_build.py init pypi
    # init `[prj]:/pypi_self` folder
    pox build/self_build.py init pypi_self
"""
import os
import sys
from collections import defaultdict
from os.path import exists
from sys import executable

from argsense import cli
from lk_utils import dumps
from lk_utils import fs
from lk_utils import run_cmd_args
from lk_utils import xpath

if 1:
    pypi_root = xpath('../chore/pypi_clean')
    os.environ['DEPSLAND_PYPI_ROOT'] = pypi_root

if 2:
    try:
        from depsland import normalization as norm
        from depsland import pypi
        from depsland import rebuild_pypi_index
        from depsland.venv import link_venv
    except AssertionError:
        print(
            ':v3',
            '`~/pypi/index/*` is not ready. you may run '
            '`py build/self_build.py init` first!',
        )


@cli.cmd('init')
def init_pypi_index(target_dir: str = 'pypi') -> None:
    """
    target_dir: `<proj>/pypi` or `<proj>/chore/pypi_clean`
    """
    fs.make_dir(f'{target_dir}/cache')
    fs.make_dir(f'{target_dir}/downloads')
    fs.make_dir(f'{target_dir}/index')
    fs.make_dir(f'{target_dir}/installed')
    
    dumps('', f'{target_dir}/cache/.gitkeep', 'plain')
    dumps('', f'{target_dir}/downloads/.gitkeep', 'plain')
    dumps('', f'{target_dir}/index/.gitkeep', 'plain')
    dumps('', f'{target_dir}/installed/.gitkeep', 'plain')
    
    dumps({}, f'{target_dir}/index/id_2_paths.json')
    dumps({}, f'{target_dir}/index/id_2_paths.pkl')
    dumps(defaultdict(set), f'{target_dir}/index/name_2_ids.pkl')
    
    print('index initialized.')


@cli.cmd('build')
def build_depsland_dependencies(
    skip_download: bool = False,
    skip_install: bool = False,
) -> None:
    """
    kwargs:
        skip_download (-sd):
        skip_install (-si):
    """
    run_cmd_args(executable, '-V')
    run_cmd_args(executable, '-m', 'pip', '-V')
    if not skip_download:
        _download(f'{pypi_root}/downloads')
    if not skip_install:
        _install(
            f'{pypi_root}/downloads',
            f'{pypi_root}/installed',
        )
    rebuild_pypi_index()


@cli.cmd()
def help_me_choose_pyversion() -> None:
    match sys.platform:
        case 'darwin':
            link = (
                'https://github.com/indygreg/python-build-standalone/releases/'
                'download/20240107/cpython-3.11.7+20240107-x86_64-apple-darwin-'
                'install_only.tar.gz'
            )
        case 'linux':
            link = (
                'https://github.com/indygreg/python-build-standalone/releases/'
                'download/20240107/cpython-3.11.7+20240107-x86_64-unknown-'
                'linux-gnu-install_only.tar.gz'
            )
        case 'win32':
            link = (
                'https://github.com/indygreg/python-build-standalone/releases/'
                'download/20240107/cpython-3.11.7+20240107-x86_64-pc-windows-'
                'msvc-shared-install_only.tar.gz'
            )
        case _:
            return
    print('please manually download python standalone from:')
    print('    ' + link)


def _download(dir_o: str) -> None:
    run_cmd_args(
        (executable, '-m', 'pip'),
        (
            'download',
            '-d',
            dir_o,
            '-r',
            xpath('../requirements.txt'),
            '-f',
            xpath('../chore/custom_packages'),
            '-f',
            dir_o,
            '-i',
            'https://pypi.tuna.tsinghua.edu.cn/simple',
        ),
        verbose=True,
    )


def _install(dir_i: str, dir_o: str) -> None:
    for f in fs.find_files(dir_i):
        if f.name.startswith('.'):
            continue
        name, ver = norm.split_filename_of_package(f.name)
        d = f'{dir_o}/{name}/{ver}'
        if exists(d):
            continue
        fs.make_dirs(d)
        run_cmd_args(
            (executable, '-m', 'pip'),
            (
                'install',
                f.path,
                '-t',
                d,
                '--no-warn-script-location',
                '--no-deps',
                '--no-index',
            ),
            verbose=True,
        )


@cli.cmd('link')
def soft_link_to_site_packages(
    target_dir: str = xpath('../python/Lib/site-packages'),
) -> None:
    """
    kwargs:
        target_dir (-t):
    """
    # print(pypi.name_2_versions, ':lv')
    
    origin_name_ids = []
    names = (
        'argsense',
        'conflore',
        'lk_logger',
        'lk_utils',
        'oss2',
        'pyyaml',
        'qmlease',
        'semver',
    )
    for n in names:
        # print(n)
        v = pypi.name_2_versions[n][0]
        nid = f'{n}-{v}'
        origin_name_ids.append(nid)
    print(':l', origin_name_ids, len(origin_name_ids))
    
    all_name_ids = set()
    for nid in origin_name_ids:
        all_name_ids.add(nid)
        all_name_ids.update(pypi.dependencies[nid]['resolved'])
    all_name_ids = list(all_name_ids)
    print(':l', all_name_ids, len(all_name_ids))
    
    link_venv(all_name_ids, venv_dir=target_dir)


if __name__ == '__main__':
    # pox build/self_build.py init
    # pox build/self_build.py help-me-choose-pyversion
    cli.run()
