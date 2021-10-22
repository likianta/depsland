# NOTE: do not encrypt this file when packaging depsland.
import sys

from os import path as ospath
from sys import path as syspath

__all__ = ['setup_env']

_curr_dir = ospath.dirname(__file__)
_lib_dir = ospath.abspath(f'{_curr_dir}/../../lib')
_build_dir = ospath.abspath(f'{_curr_dir}/../../build')


def add_pyportable_runtime():
    """ Add `~/lib/pyportable_runtime` to sys.path
     
    Tree like:
        |= src
           |= depsland
              |- __init__.py
              |- doctor.py          # 1. here we located
              |~ ...
        |= lib                      # 2. add this dir to sys.path
           |= pyportable_runtime    # 3. then this package is importable
    """
    if ospath.exists(_lib_dir):
        syspath.append(_lib_dir)
    else:
        raise ModuleNotFoundError


def setup_env():
    add_pyportable_runtime()
    
    try:
        # noinspection PyUnresolvedReferences
        import pyportable_runtime
    except Exception as e:
        print('''
            Package `pyportable_runtime` is not available to use. Depsland 
            engine has been terminated.
            
            Here's the message shows recent errors:
                {error}
            
            You can try the following steps to fix this problem:
            
            - I'm using Windows 7 (32-bit)
                - The error shows 'DLL load failed...'
                    - Go to '{depsland}/windows_patch/windows-7-sp1-32bit' dir
                    - Setup 'KB2999226-x86.msu' and 'KB3063858-x86.msu'
                    - Restart your computer
                    - Retry to setup this program
                - The error shows 'api-ms-core-... is misssing'
                    - Go to '{depsland}/windows_patch/windows-7-sp1-32bit' dir
                    - Setup 'KB2999226-x86.msu'
                    - Retry to setup this program (no need to restart computer)
                
            - I'm using Windows 7 (64-bit)
                - The error shows 'DLL load failed...'
                    - Go to '{depsland}/windows_patch/windows-7-sp1-64bit' dir
                    - Setup 'KB2999226-x64.msu' and 'KB3063858-x64.msu'
                    - Restart your computer
                    - Retry to setup this program
                - The error shows 'api-ms-core-... is misssing'
                    - Go to '{depsland}/windows_patch/windows-7-sp1-64bit' dir
                    - Setup 'KB2999226-x64.msu'
                    - Retry to setup this program (no need to restart computer)
            
            - I'm using Windows 8 (32-bit)
                - Go to '{depsland}/windows_patch/windows-8-32bit' dir
                - Setup 'vcredist-2015-x86.exe'
                - Retry to setup this program (no need to restart computer)
                
            - I'm using Windows 8 (64-bit)
                - Go to '{depsland}/windows_patch/windows-8-64bit' dir
                - Setup 'vcredist-2015-x64.exe'
                - Retry to setup this program (no need to restart computer)
                
            - I have other problem
                Please contact the supplier or depsland project owner (mail to
                likianta@foxmail.com) for more help.
            
        '''.format(
            error=e,
            depsland=_build_dir.replace('\\', '/'))
        )
        
        input('Press enter to terminate progress... ')
        
        sys.exit()
    else:
        print('[Pass] Your computer is ready to setup depsland or '
              'depsland-based programs!')
