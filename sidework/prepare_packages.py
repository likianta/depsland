import sys
import typing as t

from argsense import cli
from lk_utils import run_cmd_args


@cli.cmd()
def preinstall(
    file: str, 
    dir: str, 
    platform: t.Optional[t.Literal['darwin', 'linux', 'windows']] = None,
) -> None:
    assert file.endswith('.lock'), 'only support lock file'  # TODO
    run_cmd_args(
        (sys.executable, '-m', 'pip', 'install'),
        ('-r', file),
        ('-t', dir),
        ('--platform', platform and _normalize_platform(platform) or ''),
        # ('--only-binary', ':all:'),
        '--disable-pip-version-check',
        '--no-warn-script-location',
        ignore_return=True,
        verbose=True
    )
    print(':t', 'done')


def _normalize_platform(
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
