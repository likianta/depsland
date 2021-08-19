from os.path import dirname

from lk_utils.filesniff import normpath

curr_dir = normpath(dirname(__file__))
proj_dir = dirname(curr_dir)


class ProjConf:
    pyversion = '3.9'
    pyversion_full = 'python' + pyversion.replace('.', '')
    quiet = False


class VenvConf:
    # note: in depsland v0.* versions we don't allow user to change venv home
    # directory.
    venv_home = f'{proj_dir}/venv_home/{ProjConf.pyversion_full}'
    
    bin_dir = f'{venv_home}/bin'  # include python.exe, pythonw.exe, etc.
    cache_dir = f'{venv_home}/cache'
    download_dir = f'{venv_home}/downloads'
    lib_dir = f'{venv_home}/lib'
    lib_extra_dir = f'{venv_home}/lib_extra'
    scripts_dir = f'{venv_home}/scripts'
    venv_dir = f'{venv_home}/venv'
