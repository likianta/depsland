import sys
import typing as t

from argsense import cli
from lk_utils import run_cmd_args

from depsland import pypi


@cli.cmd()
def preinstall(
    file: str, 
    dir: str, 
    # platform: t.Optional[t.Literal['darwin', 'linux', 'windows']] = None,
) -> None:
    assert file.endswith('.lock'), 'only support lock file'  # TODO
    
    # run_cmd_args(
    #     (sys.executable, '-m', 'pip', 'install'),
    #     ('-r', file),
    #     ('-t', dir),
    #     ('--platform', platform and _reformat_platform(platform) or ''),
    #     # ('--only-binary', ':all:'),
    #     '--disable-pip-version-check',
    #     '--no-warn-script-location',
    #     ignore_return=True,
    #     verbose=True
    # )

    # if platform is None or platform == sysinfo.SYSTEM:
    #     from depsland import pypi
    # else:
    #     from depsland.pip import Pip
    #     from depsland.pypi import LocalPyPI
    #     pypi = LocalPyPI(Pip(...))

    name_ids = (x for x, _ in pypi.install_all(file))
    # name_ids = (x for x, _ in pypi.install_all(file, False))  # TEST
    pypi.linking(name_ids, dir)

    print(':t', 'done')


def _reformat_platform(
    platform: t.Literal['darwin', 'linux', 'windows']
) -> str:
    if platform == 'darwin':
        return 'macosx_11_0_arm64'
    elif platform == 'linux':
        return 'manylinux2014_x86_64'
    elif platform == 'windows':
        return 'win_amd64'
    else:
        raise Exception(platform)


if __name__ == '__main__':
    # pox sidework/prepare_packages.py preinstall <file> <dir>
    cli.run()
