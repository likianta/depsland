from lk_utils import fs

from depsland import paths
from depsland.utils import make_temp_dir
from depsland.utils import ziptool

dir_i = paths.project.root
dir_o = paths.project.depsland + '/chore'

ziptool.compress_dir(f'{dir_i}/build', f'{dir_o}/build.zip')

dir_x = make_temp_dir()
fs.copy_file(f'{dir_i}/conf/depsland.yaml', f'{dir_x}/depsland.yaml')
ziptool.compress_dir(dir_x, f'{dir_o}/conf.zip')

ziptool.compress_dir(f'{dir_i}/sidework', f'{dir_o}/sidework.zip')
