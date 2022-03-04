import tarfile
from zipfile import ZipFile


def unzip_file(src_file: str, dst_dir, complete_delete=False):
    if src_file.endswith(('.whl', '.zip')):
        file_handle = ZipFile(src_file)
    elif src_file.endswith(('.tar.gz', '.tar')):
        # https://www.cnblogs.com/xiao987334176/p/10227480.html
        file_handle = tarfile.open(src_file)
    else:
        raise Exception('Unknown file type', src_file)
    
    file_handle.extractall(dst_dir)
    
    if complete_delete:
        # delete zip file
        from os import remove
        remove(src_file)
    
    return dst_dir
