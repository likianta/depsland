"""
readme: wiki/launcher-icon-setting.md
TODO: support svg.
"""
import icnsutil
import os
from PIL import Image
from argsense import cli
from depsland.utils import make_temp_dir
from lk_utils import fs


@cli.cmd('all')
def icns_2_all(file_i: str, name_o: str = None) -> None:
    assert file_i.endswith('.icns')
    a, b, c = fs.split(file_i, 3)
    if name_o is None: name_o = b
    file_png = '{}/{}.png'.format(a, name_o)
    file_ico = '{}/{}.ico'.format(a, name_o)
    icns_2_png(file_i, file_png)
    png_2_ico(file_png, file_ico)


@cli.cmd('icns-2-ico')
def icns_2_ico(file_i: str, file_o: str = None) -> str:
    file_m = icns_2_png(file_i)
    png_2_ico(file_m, file_o or fs.replace_ext(file_i, 'png'))
    fs.remove_file(file_m)
    return file_o


@cli.cmd('icns-2-png')
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
    
    if file_o is None:
        file_o = fs.replace_ext(file_i, 'png')
    for possible_name in (
        '256x256.png',
        '256x256@2x.png',
        '512x512.png',
        '512x512@2x.png',
        '128x128.png',
        '128x128@2x.png',
    ):
        if possible_name in results:
            print(':v', f'found "{possible_name}" available')
            fs.move(f'{x}/{possible_name}', file_o, True)
            break
    else:
        raise FileNotFoundError(results)
    
    return file_o


@cli.cmd('png-2-ico')
def png_2_ico(file_i: str, file_o: str) -> str:
    """
    https://zhuanlan.zhihu.com/p/345770773
    """
    img = Image.open(file_i).resize((256, 256))
    img.save(file_o, 'ICO')
    return file_o


if __name__ == '__main__':
    # pox sidework/image_converter.py -h
    # pox sidework/image_converter.py all $icns_file
    # pox sidework/image_converter.py all $icns_file $new_name
    # pox sidework/image_converter.py icns-2-ico $icns_file
    cli.run()
