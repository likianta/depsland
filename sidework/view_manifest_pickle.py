from argsense import cli
from lk_utils import loads


@cli.cmd()
def main(pkl_file: str):
    print(loads(pkl_file), ':l')


if __name__ == '__main__':
    cli.run(main)
