import os
from collections import defaultdict

from argsense import cli
from lk_utils import dumps
from lk_utils import xpath


@cli.cmd()
def init_index():
    root_dir = xpath('../pypi/index')
    if not os.path.exists(root_dir):
        os.mkdir(root_dir)
    
    dumps(defaultdict(list), f'{root_dir}/dependencies.pkl')
    dumps(defaultdict(list), f'{root_dir}/name_2_versions.pkl')
    dumps({}, f'{root_dir}/name_id_2_paths.pkl')
    dumps({}, f'{root_dir}/updates.pkl')
    
    print(f'index initialized. see {root_dir}')


if __name__ == '__main__':
    cli.run()
