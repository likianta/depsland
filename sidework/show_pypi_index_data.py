from pprint import pprint

from lk_logger import lk
from lk_utils import dumps

from depsland.path_struct import pypi_struct


def main(save_json=False):
    a, b, c, d = pypi_struct.load_indexed_data()
    
    lk.logd('name_version')
    pprint(a)
    
    lk.logd('locations')
    pprint(b)
    
    lk.logd('dependencies')
    pprint(c)
    
    lk.logd('updates')
    pprint(d)
    
    if save_json:
        for data, file in zip(
                (a, b, c, d),
                pypi_struct.get_indexed_files()
        ):
            dumps(data, file.removesuffix('.pkl') + '.json')


if __name__ == '__main__':
    main(True)
