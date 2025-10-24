from lk_utils import fs

compress_dir = fs.zip_dir


def extract_file(file_i: str, path_o: str, overwrite: bool = None) -> str:
    if file_i.endswith('.fzip'):
        fs.copy_file(file_i, path_o, overwrite=overwrite)
        return path_o
    else:
        return fs.unzip_file(file_i, path_o, overwrite)
