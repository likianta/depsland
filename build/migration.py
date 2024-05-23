import os

from argsense import cli
from lk_utils import fs

os.environ['DEPSLAND_PYPI_ROOT'] = 'pypi'

from depsland.pypi.insight import rebuild_index
from depsland.normalization import split_filename_of_package


@cli.cmd()
def remove_unsatisfied_whl_files(
    target_version: str = '3.12'
) -> None:
    target_code = 'cp{}'.format(target_version.replace('.', ''))
    to_be_deleted = []
    for f in fs.find_files('pypi/downloads', '.whl'):
        if f.name.split('-')[-3] not in ('py2.py3', 'py3', target_code):
            print(f.name, ':v4si')
            name, ver = split_filename_of_package(f.name)
            # to_be_deleted.append((f.path, f'pypi/installed/{name}/{ver}'))
            to_be_deleted.append((f.path, f'pypi/installed/{name}'))
    for f, d in to_be_deleted:
        fs.remove_file(f)
        fs.remove_tree(d)


@cli.cmd()
def rebuild_pypi_index() -> None:
    rebuild_index(perform_pip_install=True)


if __name__ == '__main__':
    # pox build/migration.py remove-unsatisfied-whl-files
    # pox build/migration.py rebuild-pypi-index
    cli.run()
