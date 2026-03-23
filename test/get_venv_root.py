from argsense import cli
from lk_utils import fs

from depsland.venv.target_venv import get_venv_root


@cli
def main(working_root: str) -> None:
    print(get_venv_root(fs.abspath(working_root)), ':sv2')


if __name__ == '__main__':
    cli.run(main)
