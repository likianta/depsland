from pprint import pprint

from depsland.path_struct import pypi_struct

a, b, c, d = pypi_struct.load_indexed_data()
pprint(a)
pprint(b)
pprint(c)
pprint(d)
