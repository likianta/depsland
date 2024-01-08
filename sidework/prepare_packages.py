import os
import sys
import typing as t
from os.path import exists

from argsense import cli

from depsland import pypi


@cli.cmd()
def preindex(reqlock_file: str) -> None:
    for _ in (
        x for x, _, _ in pypi.install_all(
            y for y, _ in pypi.download_all(reqlock_file)
        )
    ):
        # print(id, ':i')
        pass
    print(':t', 'done')


@cli.cmd()
def preinstall(
    file: str,
    dir: str,
    # platform: t.Optional[t.Literal['darwin', 'linux', 'windows']] = None,
) -> None:
    assert file.endswith('.lock'), 'only support lock file'  # TODO
    if exists(dir) and os.listdir(dir):
        print('make sure the target directory not exists or be empty')
        sys.exit(0)
    name_ids = (
        x for x, _, _ in pypi.install_all(
            y for y, _ in pypi.download_all(file)
        )
    )
    pypi.linking(name_ids, dir)
    # # pypi.linking(name_ids, dir, overwrite=True)
    
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
    # pox sidework/prepare_packages.py preindex <file>
    # pox sidework/prepare_packages.py preinstall <file> <dir>
    cli.run()
