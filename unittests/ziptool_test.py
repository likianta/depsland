import os
from argsense import cli
from depsland import utils
from depsland.utils import ziptool


@cli.cmd()
def test_unzip_and_move_up():
    a = utils.create_temporary_directory()
    b = f'{a}/b'
    c = f'{a}/b/c.txt'
    d = f'{a}/d.zip'
    e = f'{a}/e'
    f = f'{a}/e/b'
    
    os.mkdir(b)
    open(c, 'w').close()
    print(os.listdir(b))
    
    ziptool.compress_dir(b, d, overwrite=True)
    
    os.mkdir(e)
    ziptool.unzip_file(d, f, overwrite=True)
    
    print(f'check {f}, see if it empty')
    print(os.listdir(f))
    # assert os.listdir(f) == ['c.txt']


if __name__ == '__main__':
    cli.run()