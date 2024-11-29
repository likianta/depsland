import sys

import lk_logger
from argsense import cli

lk_logger.setup(quiet=True, show_varnames=True)


@cli.cmd()
def check_args(*args, **kwargs):
    print(sys.argv, ':l')
    print(args, kwargs, ':l')


if __name__ == '__main__':
    cli.run()
