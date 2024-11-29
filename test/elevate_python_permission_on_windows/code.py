import ctypes
import os
import sys

from argsense import cli


@cli.cmd()
def main(uac=False) -> None:
    if uac:
        print(sys.argv)
        run_as_admin(sys.argv[0])
        return
    
    with open('aaa.txt', 'w') as a:
        a.write('aaa')
    
    try:
        os.symlink('aaa.txt', 'bbb.txt')
    except OSError as e:
        print(f'symlink doesnot work: {e}')
        print('you need to run this script in administrator role.')
    else:
        print('you have the right access')
        os.unlink('bbb.txt')
    finally:
        os.remove('aaa.txt')
    
    input('press enter to close: ')


def run_as_admin(cmd_line: str) -> int:
    """
    https://stackoverflow.com/a/33856172
    """
    shell32 = ctypes.windll.shell32
    py_exec = sys.executable
    # py_exec = sys.executable.replace('python.exe', 'pythonw.exe')
    print(py_exec, cmd_line)
    ret = shell32.ShellExecuteW(None, "runas", py_exec, cmd_line, None, 1)
    print(ret)
    return 0 if ret > 32 else ret  # return the error code


if __name__ == '__main__':
    cli.run(main)
