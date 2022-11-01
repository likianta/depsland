if 1:
    import sys
    from lk_utils import xpath
    sys.path.insert(0, xpath('..', True))

import os
from collections import defaultdict
from os.path import exists

from argsense import cli
from lk_utils import dumps
from lk_utils import fs

from depsland import __version__
from depsland import paths
from depsland.utils import ziptool

print(':v2', f'depsland version: {__version__}')


@cli.cmd()
def build(add_python_path=True):
    root_i = paths.project.root
    root_o = '{dist}/{version}'.format(
        dist=paths.project.dist,
        version=f'depsland-{__version__}'
    )
    assert not exists(root_o)
    os.mkdir(root_o)
    
    # make empty dirs
    os.mkdir(f'{root_o}/apps')
    os.mkdir(f'{root_o}/apps_launcher')
    os.mkdir(f'{root_o}/build')
    os.mkdir(f'{root_o}/build/exe')
    os.mkdir(f'{root_o}/conf')
    # os.mkdir(f'{root_o}/depsland')
    os.mkdir(f'{root_o}/docs')
    os.mkdir(f'{root_o}/pypi')
    os.mkdir(f'{root_o}/pypi/cache')
    os.mkdir(f'{root_o}/pypi/downloads')
    os.mkdir(f'{root_o}/pypi/index')
    os.mkdir(f'{root_o}/pypi/installed')
    # os.mkdir(f'{root_o}/python')
    # os.mkdir(f'{root_o}/sidework')
    os.mkdir(f'{root_o}/temp')
    os.mkdir(f'{root_o}/temp/.fake_oss_storage')
    os.mkdir(f'{root_o}/temp/.unittests')
    
    # copy files
    fs.copy_file(f'{root_i}/build/exe/depsland.exe',
                 f'{root_o}/build/exe/depsland.exe')
    fs.copy_file(f'{root_i}/build/exe/setup.exe',
                 f'{root_o}/setup.exe')
    fs.copy_file(f'{root_i}/build/depsland_setup.py',
                 f'{root_o}/build/depsland_setup.py')
    fs.copy_file(f'{root_i}/conf/depsland.yaml',
                 f'{root_o}/conf/depsland.yaml')
    fs.copy_file(f'{root_i}/conf/oss_client.yaml',
                 f'{root_o}/conf/oss_client.yaml')
    fs.copy_tree(f'{root_i}/depsland',
                 f'{root_o}/depsland')
    fs.copy_tree(f'{root_i}/sidework',
                 f'{root_o}/sidework')
    if add_python_path:
        fs.make_link(f'{root_i}/python',
                     f'{root_o}/python')
    
    # init files
    dumps(defaultdict(list), f'{root_o}/pypi/index/dependencies.pkl')
    dumps(defaultdict(list), f'{root_o}/pypi/index/name_2_versions.pkl')
    dumps({}, f'{root_o}/pypi/index/name_id_2_paths.pkl')
    dumps({}, f'{root_o}/pypi/index/updates.pkl')
    
    print(':t', 'see result at', fs.relpath(root_o))


@cli.cmd()
def compress_to_zip():
    dir_i = '{}/{}'.format(paths.project.dist, f'depsland-{__version__}')
    file_o = '{}/{}'.format(paths.project.dist, f'depsland-{__version__}.zip')
    ziptool.compress_dir(dir_i, file_o, overwrite=True)
    print(':t', 'see result at', fs.relpath(file_o))


if __name__ == '__main__':
    cli.run()
