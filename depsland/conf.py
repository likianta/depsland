from os.path import dirname

from lk_utils.filesniff import normpath

curr_dir = normpath(dirname(__file__))


class DefaultConf:
    pyversion = '3.9'
    pyversion_full = 'python' + pyversion.replace('.', '')


class VenvConf:
    # see `../docs/project-structure.md`
    venv_home = normpath(
        f'{curr_dir}/../depsland_venv/{DefaultConf.pyversion_full}'
    )  # TODO: fetch home dir from `os.env`
    bin_dir = f'{venv_home}/bin'  # include python.exe, pythonw.exe, etc.
    download_dir = f'{venv_home}/downloads'
    lib_dir = f'{venv_home}/lib'  # equals to 'site-packages'
    scripts_dir = f'{venv_home}/scripts'
    venv_dir = f'{venv_home}/venv'
