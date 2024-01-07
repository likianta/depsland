from argsense import cli

from depsland import rebuild_pypi_index
from depsland.pypi.insight import overview

cli.add_cmd(overview)
cli.add_cmd(rebuild_pypi_index, 'rebuild')

if __name__ == '__main__':
    # pox side_work/pypi_index.py rebuild
    cli.run()
