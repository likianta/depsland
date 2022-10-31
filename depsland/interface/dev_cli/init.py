import os
import re
from os.path import exists

from lk_utils import dumps
from lk_utils import fs
from lk_utils import loads

from ...manifest import T


def init(
        manifest: str = './manifest.json',
        appname='',
        overwrite=False,
        auto_find_requirements=False
):
    """
    kwargs:
        manifest (-m): if directory of manifest not exists, it will be created.
        appname (-n): if not given, will use directory name as app name.
        auto_find_requirements (-a):
        overwrite (-o):
    """
    # init/update parameters
    filepath = fs.normpath(manifest, True)
    dirpath = fs.parent_path(filepath)
    dirname = fs.dirname(dirpath)
    if appname == '':
        appname = dirname.replace('-', ' ').replace('_', ' ').title()
    appid = appname.replace(' ', '_').replace('-', '_').lower()
    print(':v2', appname, appid)
    
    # check path exists
    if not exists(dirpath):
        os.mkdir(dirpath)
    if exists(filepath):
        if overwrite:
            os.remove(filepath)
        else:
            r = input(f'target file ({filepath}) already exists, would '
                      f'you like to overwrite it? (y/n): ')
            if r == 'y':
                os.remove(filepath)
            else:
                print('[dim]no file creates[/]', ':r')
                return
    
    manifest: T.Manifest = {
        'appid'       : appid,
        'name'        : appname,
        'version'     : '0.1.0',
        'assets'      : {},
        'dependencies': {},
    }
    
    if auto_find_requirements:
        if exists(x := f'{dirpath}/requirements.txt'):
            pattern = re.compile(r'([-\w]+)(.*)')
            deps = manifest['dependencies']
            for line in loads(x).splitlines():  # type: str
                if line and not line.startswith('#'):
                    name, ver = pattern.search(line).groups()
                    deps[name] = ver.replace(' ', '')
            print(deps, ':l')
    
    dumps(manifest, x := f'{dirpath}/manifest.json')
    print(f'see manifest file at \n\t"{x}"')
