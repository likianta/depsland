import os
from depsland import config
from depsland import paths
from depsland.interface.user_cli.install import install
from lk_utils import fs
from lk_utils.time_utils import timestamp
from lk_utils import loads

config.debug_mode = True
appid = 'batchreg'

history = loads(f'{paths.Project.apps}/{appid}/released_history.json')
local_latest_version: str = history[0]

if os.path.exists(d := f'{paths.Project.apps}/{appid}/{local_latest_version}'):
    dir_i = d
    dir_o = d + '_' + timestamp('hns')
    print('backup local dir', '{} -> {}'.format(
        fs.basename(dir_i), fs.basename(dir_o)
    ))
    fs.move(dir_i, dir_o)

# note: if pypi raised error, better to manually delete `paths.pypi.index`
#   folder before next try.
install(appid)
