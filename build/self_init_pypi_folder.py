"""
init `~/pypi` folder based on depsland's own requirements.
requirements:
    - argsense
    - lk-utils
"""
from sys import executable

from argsense import cli
from lk_utils import xpath
from lk_utils.subproc import compose_cmd
from lk_utils.subproc import run_cmd_args

from depsland import rebuild_pypi_index


@cli.cmd()
def main(skip_download=False) -> None:
    """
    kwargs:
        skip_download (-s):
    """
    run_cmd_args(executable, '-V')
    if not skip_download:
        run_cmd_args(executable, '-m', 'pip', '-V')
        run_cmd_args(
            *compose_cmd(
                (executable, '-m', 'pip'),
                ('download',
                 '-d', xpath('../pypi/downloads'),
                 '-r', xpath('../requirements.txt'),
                 '-f', xpath('../chore/custom_packages'),
                 '-f', xpath('../pypi/downloads'),
                 '-i', 'https://pypi.tuna.tsinghua.edu.cn/simple'),
            ),
            verbose=True
        )
    rebuild_pypi_index()


if __name__ == '__main__':
    cli.run(main)
