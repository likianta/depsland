from lk_logger.console import con_print
from lk_utils import fs
from rich.table import Table

from ..paths import pypi as pypi_paths
from ..pypi import insight
from ..utils import verspec


def rebuild_index(perform_pip_install: bool = False) -> None:
    insight.rebuild_index(perform_pip_install)
    table = MyTable()
    for f in fs.find_files(pypi_paths.downloads):
        if f.name != '.gitkeep':
            ver = verspec.get_verspec_from_filename(f.name)
            table.update(f.name, ver.name, ver.version)
    table.render()
    print(':t')


class MyTable:
    
    def __init__(self):
        self.table = Table()
        self.table.add_column('index')
        self.table.add_column('filename')
        self.table.add_column('name', style='green')
        self.table.add_column('version', style='cyan')
        self._table_index = 0
    
    def update(self, filename: str, pakgname: str, version: str) -> None:
        self._table_index += 1
        self.table.add_row(str(self._table_index), filename, pakgname, version)
    
    def render(self) -> None:
        print(':f2')
        con_print(self.table)
