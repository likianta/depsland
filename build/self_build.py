"""
init `~/pypi` folder based on depsland's own requirements.
requirements:
    - argsense
    - lk-utils
"""
import os
from collections import defaultdict
from sys import executable

from argsense import cli
from lk_utils import dumps
from lk_utils import fs
from lk_utils import xpath
from lk_utils.subproc import compose_cmd
from lk_utils.subproc import run_cmd_args

try:
    from depsland import normalization as norm
    from depsland import rebuild_pypi_index
except AssertionError:
    print(':v3', '`~/pypi/index/*` is not ready. you may run '
                 '`py build/self_build.py init` first!')


@cli.cmd('init')
def init_pypi_index() -> None:
    root_dir = xpath('../pypi/index')
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
    
    dumps(defaultdict(list), f'{root_dir}/dependencies.pkl')
    dumps(defaultdict(list), f'{root_dir}/name_2_versions.pkl')
    dumps({}, f'{root_dir}/name_id_2_paths.pkl')
    dumps({}, f'{root_dir}/updates.pkl')
    
    print(f'index initialized. see {root_dir}')


@cli.cmd('build')
def build_depsland_dependencies(
        skip_download=False,
        skip_install=False,
        target_root=xpath('../pypi')
) -> None:
    """
    kwargs:
        skip_download (-sd):
        skip_install (-si):
    """
    run_cmd_args(executable, '-V')
    run_cmd_args(executable, '-m', 'pip', '-V')
    if not skip_download:
        _download(f'{target_root}/downloads')
    if not skip_install:
        _install(
            f'{target_root}/downloads',
            f'{target_root}/installed',
        )
    rebuild_pypi_index()


def _download(dir_o: str) -> None:
    run_cmd_args(
        *compose_cmd(
            (executable, '-m', 'pip'),
            ('download',
             '-d', dir_o,
             '-r', xpath('../requirements.txt'),
             '-f', xpath('../chore/custom_packages'),
             '-f', dir_o,
             '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'),
        ),
        verbose=True
    )


def _install(dir_i: str, dir_o: str) -> None:
    for f in fs.find_files(dir_i):
        if f.name.startswith('.'): continue
        name, ver = norm.filename_2_name_version(f.name)
        d = f'{dir_o}/{name}/{ver}'
        fs.make_dirs(d)
        run_cmd_args(
            *compose_cmd(
                (executable, '-m', 'pip'),
                ('install',
                 f.path,
                 '-t', d,
                 '--no-warn-script-location',
                 '--no-deps',
                 '--no-index')
            ),
            verbose=True
        )


if __name__ == '__main__':
    cli.run()
