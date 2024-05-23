"""
readme: wiki/launcher-icon-setting.md
requirements:
    - argsense
    - depsland
    - icnsutil
    - lk-utils
    - pillow
TODO: support svg.
"""
import os
import typing as t
from functools import wraps
from types import FunctionType

import icnsutil
from PIL import Image
from argsense import cli
from lk_utils import fs

from depsland.utils import make_temp_dir


class T:
    Extension = t.Literal['icns', 'ico', 'png']
    Function = t.TypeVar('Function', bound=FunctionType)


def _correct_io(ext: T.Extension) -> t.Callable[[T.Function], T.Function]:
    def decorator(func: T.Function) -> t.Callable[[str, str], None]:
        @wraps(func)
        def wrapper(file_i: str, file_o: str = None) -> None:
            file_i = fs.normpath(file_i)
            if not file_o:
                file_o = fs.replace_ext(file_i, ext)
            return func(file_i, file_o)
        
        return wrapper
    
    return t.cast(t.Callable[[T.Function], T.Function], decorator)


@cli.cmd('all')
def icns_2_all(file_i: str, name_o: str = None) -> None:
    assert file_i.endswith('.icns')
    if not name_o:
        name_o = fs.basename(file_i, False)
    file_m = icns_2_png(file_i, '{}/{}.png'.format(fs.parent(file_i), name_o))
    png_2_ico(file_m, '{}/{}.ico'.format(fs.parent(file_i), name_o))


@cli.cmd('icns-2-ico')
@_correct_io('ico')
def icns_2_ico(file_i: str, file_o: str) -> str:
    file_m = icns_2_png(file_i, '')
    png_2_ico(file_m, file_o)
    fs.remove_file(file_m)
    return file_o


@cli.cmd('icns-2-png')
@_correct_io('png')
def icns_2_png(file_i: str, file_o: str) -> str:
    """
    https://pypi.org/project/icnsutil/
    https://blog.csdn.net/qq_34146694/article/details/127251404
    """
    img = icnsutil.IcnsFile(file_i)
    img.export(
        x := make_temp_dir(),
        allowed_ext='png',
        recursive=True,
        convert_png=True,
    )
    
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
            fs.move(f'{x}/{possible_name}', file_o, True)
            break
    else:
        raise FileNotFoundError(results)
    
    _print_done(file_o)
    return file_o


@cli.cmd('png-2-ico')
@_correct_io('ico')
def png_2_ico(file_i: str, file_o: str) -> str:
    """
    https://zhuanlan.zhihu.com/p/345770773
    """
    img = Image.open(file_i).resize((256, 256))
    img.save(file_o, 'ICO')
    _print_done(file_o)
    return file_o


def _print_done(file_o: str) -> None:
    print(':trpi', f'[green]conversion done. see result at "{file_o}"[/]')


if __name__ == '__main__':
    # pox sidework/image_converter.py -h
    # pox sidework/image_converter.py all $icns_file
    # pox sidework/image_converter.py all $icns_file $new_name
    # pox sidework/image_converter.py icns-2-ico $icns_file
    cli.run()
