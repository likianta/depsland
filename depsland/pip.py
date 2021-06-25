import subprocess

from .conf import DefaultConf, VenvConf


class Pip:
    
    def __init__(
            self,
            local='',
            offline=False,
            pypi_url='https://pypi.python.org/simple/',
            pyversion=DefaultConf.pyversion,
            quiet=True,
            # target=VenvConf.lib_dir,
    ):
        if offline is False:
            assert pypi_url
            host = pypi_url \
                .removeprefix('http://') \
                .removeprefix('https://') \
                .split('/', 1)[0]
        else:
            host = ''
        
        # setup options
        self.template = ' '.join((
            f'pip {{action}} {{name}} --target="{{target}}"',
            f'--disable-pip-version-check',
            f'--find-links="{local}"' if local else '',
            f'--index-url {pypi_url}' if not offline else '',
            f'--no-index' if offline else '',
            f'--only-binary=:all:',
            f'--python-version {pyversion}' if pyversion else '',
            f'--quiet' if quiet else '',
            f'--trusted-host {host}' if host else '',
        ))

    def install(self, name: str, target=VenvConf.lib_dir):
        """ install package to `VenvConf.lib_dir` (default). """
        send_cmd(self.template.format(
            action='install', name=name, target=target
        ), ignore_errors=False)
    
    def download(self, name: str, target=VenvConf.download_dir):
        send_cmd(self.template.format(
            action='download', name=name, target=target
        ), ignore_errors=False)
        

def send_cmd(cmd: str, ignore_errors=False):
    """

    Args:
        cmd:
        ignore_errors

    References:
        https://docs.python.org/zh-cn/3/library/subprocess.html
    """
    try:
        '''
        subprocess.run:params
            shell=True  传入字符串, 以字符串方式调用命令
            shell=False 传入一个列表, 列表的第一个元素当作命令, 后续元素当作该命
                        令的参数
            check=True  检查返回码, 如果 subprocess 正常运行完, 则返回码是 0. 如
                        果有异常发生, 则返回码非 0. 当返回码非 0 时, 会报
                        `subprocess.CalledProcessError` 错误
            capture_output=True
                        捕获输出后, 控制台不会打印; 通过:
                            output = subprocess.run(..., capture_output=True)
                            output.stdout.read()  # -> bytes ...
                            output.stderr.read()  # -> bytes ...
                        可以获取.
        '''
        from lk_logger import lk
        lk.log(cmd.replace(VenvConf.venv_home, '~'))
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        if ignore_errors:
            return False
        else:
            raise Exception(e.stderr)
    else:
        return True
