# DELETE
import os
import typing as t
from functools import partial
from urllib import request


class T:
    Overwrite = t.Union[bool, None]


def download(dst: str, src: str, overwrite: T.Overwrite = None) -> None:
    if os.path.exists(src):
        match overwrite:
            case None:  # skip
                return
            case True:  # overwrite
                os.remove(src)
            case False:  # raise error
                raise FileExistsError(src)
    
    # https://blog.csdn.net/weixin_39790282/article/details/90170218
    # noinspection PyTypeChecker
    request.urlretrieve(dst, src, partial(_progress, f'downloading {src}'))
    print(f'done ({src}', ':t')


def _progress(
        description: str,
        block_num: int, block_size: int, total_size: int
) -> None:
    print('{}: {:.2%}'.format(
        description,
        block_num * block_size / total_size,
    ), end='\r')
