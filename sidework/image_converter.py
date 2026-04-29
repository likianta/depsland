"""
TODO: support svg.
"""

import icnsutil
import os
from PIL import Image
from argsense import cli
from depsland.utils import make_temp_dir
from lk_utils import fs


@cli
def main(file_i: str, file_o: str = '') -> None:
    """
    params:
        file_i (-i):
        file_o (-o):
            if not given, use the same directory as file_i.
            if given directory, use the same filename as file_i.
            if given path, make sure it ends with '.png' or '.ico'.
            if given `Literal['.ico', '.png']`, convert it to the according
            format.
    """
    assert file_i.endswith(('.icns', '.png'))
    if file_o:
        if file_o in ('.ico', '.png'):
            file_o = fs.replace_ext(file_i, file_o[1:])
        elif fs.isdir(file_o):
            file_o = '{}/{}'.format(file_o, fs.basename(file_i))
        else:
            assert file_o.endswith(('.ico', '.png'))
    else:
        if file_i.endswith('.icns'):
            file_png = icns_2_png(file_i, fs.replace_ext(file_i, 'png'))
            file_ico = png_2_ico(file_png, fs.replace_ext(file_i, 'ico'))
            print('results: \n    {}\n    {}'.format(file_png, file_ico), ':v4')
            return
        file_o = fs.replace_ext(file_i, 'ico')

    if file_i.endswith('.icns'):
        if file_o.endswith('.ico'):
            icns_2_ico(file_i, file_o)
        else:
            icns_2_png(file_i, file_o)
    else:
        png_2_ico(file_i, file_o)

    print('result: {}'.format(file_o), ':v4')


@cli
def extract_icns(file_i: str, name_o: str = '') -> None:
    assert file_i.endswith('.icns')
    a, b, c = fs.split(file_i, 3)  # type: ignore
    if not name_o:
        name_o = b
    file_png = '{}/{}.png'.format(a, name_o)
    file_ico = '{}/{}.ico'.format(a, name_o)
    icns_2_png(file_i, file_png)
    png_2_ico(file_png, file_ico)


@cli
def icns_2_ico(file_i: str, file_o: str = '') -> str:
    if not file_o:
        file_o = fs.replace_ext(file_i, 'ico')
    file_m = icns_2_png(file_i, fs.replace_ext(file_i, 'png'))
    png_2_ico(file_m, file_o)
    fs.remove_file(file_m)
    return file_o


@cli
def icns_2_png(file_i: str, file_o: str = '') -> str:
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

    if not file_o:
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


@cli
def png_2_ico(file_i: str, file_o: str = '') -> str:
    """
    https://zhuanlan.zhihu.com/p/345770773
    """
    if not file_o:
        file_o = fs.replace_ext(file_i, 'ico')
    img = Image.open(file_i).resize((256, 256))
    img.save(file_o, 'ICO')
    return file_o


if __name__ == '__main__':
    # pox sidework/image_converter.py -h
    cli.run()
