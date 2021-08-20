import os
from time import strftime
from urllib import request

from lk_logger import lk


def download(link, file, exist_ok=True):
    """ See animated gif `~/docs/.assets/downloading-embed-python-anim.gif`
    """
    if os.path.exists(file):
        if exist_ok:
            lk.loga('file already exists (pass)', file)
            return
        else:
            raise FileExistsError(file)
    
    lk.loga('downloading', link)
    lk.loga('waiting for downloader starts...')
    # https://blog.csdn.net/weixin_39790282/article/details/90170218
    request.urlretrieve(link, file, _update_progress)
    lk.loga('done')


def _update_progress(block_num, block_size, total_size):
    """

    Args:
        block_num: downloaded data blocks number
        block_size: size of each block
        total_size: total size of remote file in url
    """
    percent = block_size * block_num / total_size * 100
    if percent > 100: percent = 100
    print('\r{}\t{:.2f}%'.format(strftime('%H:%M:%S'), percent), end='')
    #   why put `\r` in the first param?
    #       because it doesn't work in pycharm if we pass it to `params:end`
    #       ref: https://stackoverflow.com/questions/34950201/pycharm-print-end
    #            -r-statement-not-working
