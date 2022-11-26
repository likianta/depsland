"""
requirements:
    - argsense
    - depsland
    - icnsutil
    - lk-utils
    - pillow
"""
import os

import icnsutil
from PIL import Image
from argsense import cli
from lk_utils import fs

from depsland.utils import make_temp_dir


@cli.cmd()
def main(file_i: str, file_o: str = None) -> None:
    file_i = fs.normpath(file_i)
    dir_ = fs.dirpath(file_i)
    name = fs.filename(file_i, False)
    if file_o is None:
        file_o = f'{dir_}/{name}.ico'
    
    print('convert from {} to {}'.format(
        fs.filename(file_i), fs.filename(file_o)
    ))
    
    if file_i.endswith('.icns') and file_o.endswith('.ico'):
        i, m, o = file_i, f'{dir_}/{name}.png', file_o
        _icns_2_png(i, m)
        _png_2_ico(m, o)
        fs.remove_file(m)
    else:
        raise NotImplementedError()
    
    print(':tr', f'[green]done. see converted icon at "{file_o}"[/]')


def _icns_2_png(i: str, o: str) -> None:
    """
    https://pypi.org/project/icnsutil/
    https://blog.csdn.net/qq_34146694/article/details/127251404
    """
    img = icnsutil.IcnsFile(i)
    img.export(x := make_temp_dir(),
               allowed_ext='png',
               recursive=True,
               convert_png=True)
    
    results = os.listdir(x)
    print(':v', results)
    
    for possible_name in (
            '256x256.png',
            '256x256@2x.png',
            '512x512.png',
            '512x512@2x.png',
    ):
        if possible_name in results:
            print(':v', f'found "{possible_name}" available')
            fs.move(f'{x}/{possible_name}', o, True)
            break
    else:
        raise FileNotFoundError(results)


def _png_2_ico(i: str, o: str) -> None:
    """
    https://zhuanlan.zhihu.com/p/345770773
    """
    img = Image.open(i).resize((256, 256))
    img.save(o, 'ICO')


if __name__ == '__main__':
    cli.run(main)
