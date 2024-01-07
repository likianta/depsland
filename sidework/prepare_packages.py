import os
import sys
import typing as t
from os.path import exists

from argsense import cli

from depsland import pypi


@cli.cmd()
def preindex(reqlock_file: str) -> None:
    dl_paths = tuple(x for x, _ in pypi.download_all(reqlock_file))
    ins_paths = tuple(x for _, x, _ in pypi.install_all(dl_paths))
    assert len(dl_paths) == len(ins_paths)
    for p0, p1 in zip(dl_paths, ins_paths):
        try:
            pypi.add_to_index(p0, 0)
            pypi.add_to_index(p1, 1)
        except Exception as e:
            print(p0, p1, ':lv4')
            raise e
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
    
    name_ids = (
        x for x, _ in pypi.install_all(
            y for y, _, _ in pypi.download_all(file)
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
