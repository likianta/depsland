from pprint import pprint

from lk_logger import lk
from lk_utils import dumps

from depsland.paths import pypi_model


def main(save_json=False):
    a, b, c, d = pypi_model.load_indexed_data()
    
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
                pypi_model.get_indexed_files()
        ):
            dumps(data, file.replace('.pkl', '.json'))


if __name__ == '__main__':
    main(True)
