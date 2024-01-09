from collections import defaultdict

from argsense import cli
from lk_utils import dumps
from lk_utils import fs

from depsland import rebuild_pypi_index
from depsland.paths import pypi as pypi_paths
from depsland.pypi.insight import overview

cli.add_cmd(overview)
cli.add_cmd(rebuild_pypi_index, 'rebuild')


@cli.cmd()
def reset() -> None:
    root = pypi_paths.root
    for f in (
        'id_2_paths.json',
        'id_2_paths.pkl',
        'name_2_ids.pkl',
    ):
        fs.move(f'{root}/index/{f}', f'{root}/index/{f}.bak', True)
    dumps({}, f'{root}/index/id_2_paths.json')
    dumps({}, f'{root}/index/id_2_paths.pkl')
    dumps(defaultdict(set), f'{root}/index/name_2_ids.pkl')


if __name__ == '__main__':
    # pox sidework/pypi_index.py rebuild
    # pox sidework/pypi_index.py rebuild :true
    # pox sidework/pypi_index.py reset
    cli.run()
