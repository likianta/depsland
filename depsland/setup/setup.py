"""
Deploy depsland on client computer and make sure depsland integrity.
"""
import sys

import os
import shutil
from depsland import paths
from depsland.setup import setup_embed_python
from lk_utils import dumps
from lk_utils import loads
from os.path import dirname
from os.path import exists
from os.path import normpath
from textwrap import dedent

proj_dir = paths.project.root
platform = sys.platform.lower()

src_model = ...
assets_model = ...


def _fuzzy_find_path(name):
    parent_dir = paths.project.root
    for try_times in range(2):
        parent_dir = dirname(parent_dir)
        if exists(out := f'{parent_dir}/{name}'):
            return out
    raise FileNotFoundError(name)


def main(pyversion='python39'):
    # always refresh system environment
    env_var = _add_to_system_environment()
    
    curr_build_dir = _fuzzy_find_path('build')
    if exists(f'{curr_build_dir}/setup_done.txt'):
        print(':v2', dedent('''
            Despland has been installed on your computer.
            For re-installation, you can delete '~/build/setup_done.txt' then
            run 'setup.exe' again.
        '''))
        return
    
    src_model.indexing_dirs(pyversion)
    assets_model.indexing_dirs(pyversion)
    
    _build_dirs()
    _setup_embed_python(pyversion)
    bat_file = _create_depsland_bat()
    _mark_setup_is_done(curr_build_dir)
    _store_launching_info_in_program_data_dir(bat_file)
    
    if '%DEPSLAND%' not in os.getenv('PATH') and \
            env_var not in os.getenv('PATH'):
        print(':v2', '\n    ' + '\n    '.join((
            'THE NEXT STEP:',
            '    (Suggest) You can add "%DEPSLAND%" to your system environment '
            'PATH mannually. Then test it in the CMD:',
            '        depsland --version',
            '    There\'re should be shown "Python 3.9.7" or "Python 3.8.10". '
            '(the pyversion depends on depsland version)',
            'NOTE:',
            '    - You may restart CMD to make new environment variable '
            'settings take effect',
        )))
    print('Successfully setup depsland :)')


def _build_dirs():
    for d in (
            f'{proj_dir}/venv_home',
            f'{proj_dir}/venv_home/inventory',
            f'{proj_dir}/venv_home/inventory/{platform}',
            f'{proj_dir}/venv_home/venv_links',
            f'{proj_dir}/pypi',
            f'{proj_dir}/pypi/cache',
            f'{proj_dir}/pypi/downloads',
            f'{proj_dir}/pypi/extracted',
            f'{proj_dir}/pypi/index',
    ):
        if not exists(d):
            print('mkdir', d)
            os.mkdir(d)
    
    src_model.build_dirs()


def _setup_embed_python(pyversion):
    if not os.path.exists(src_model.python_exe):
        assert not os.path.exists(src_model.python)
        setup_embed_python(pyversion, src_model.python)
        assert os.path.exists(src_model.python_exe)


def _create_depsland_bat():
    template = loads(f'{proj_dir}/build/depsland.bat')
    code = template.format(PYTHON=sys.executable)
    dumps(code, d := f'{proj_dir}/depsland.bat')
    return d


def _mark_setup_is_done(build_dir):
    dumps('', f'{build_dir}/setup_done.txt')


def _add_to_system_environment():
    """
    References:
        https://stackoverflow.com/questions/17657686/is-it-possible-to-set-an
            -environment-variable-from-python-permanently
    
    Notice:
        1. Do not use `setx PATH "%PATH%;<DEPSLAND>"`, because we can't
           distinguish the system paths and user paths in this way.
           I will set a new environment variable named 'DEPSLAND' in user
           variables.
        2. The `setx` command is only available in Windows 7 and later.
        3. For third party file explorer/manager, for example XYPlorer, Clover
           or File Explorer UWP, new settings cannot be effected immediately
           unless the user closes the third party app and restarts it. It means
           this function only works well with Windows File Explorer.
           To resolve this issue, I will not only create a system environment
           variable, but also store the depsland entrance message in
           'C:/ProgramData' (which can be fetched by CMD `%PROGRAMDATA%`).
           See also `function:_store_launching_info_in_program_data_dir`.
    """
    depsland_entrance = normpath(proj_dir)
    os.system('setx DEPSLAND "{}"'.format(depsland_entrance))
    print(f'Added DEPSLAND to environment variable\n'
          f'DEPSLAND => {depsland_entrance}')
    return depsland_entrance


def _store_launching_info_in_program_data_dir(bat_file):
    program_data_dir = os.getenv('ProgramData')  # -> 'C:\ProgramData'
    depsland_dir = f'{program_data_dir}/Depsland'.replace('\\', '/')
    depsland_bat = f'{depsland_dir}/depsland.bat'.replace('\\', '/')
    
    assert program_data_dir is not None
    if not exists(depsland_dir):
        os.mkdir(depsland_dir)
    if exists(depsland_bat):
        os.remove(depsland_bat)
    
    shutil.copyfile(bat_file, depsland_bat)
    
    from depsland import __version__
    dumps(dedent('''
        __version__ = "{}"
        depsland_dir = r"{}"
        depsland_bat = r"{}"
    '''.format(
        __version__,
        proj_dir,
        f'{proj_dir}/depsland.bat'
    )).strip(), f'{depsland_dir}/depsland_entrance.py')
    #   see usage in pyportable-installer project:
    #       ~/template/depsland/setup_part_b.txt


if __name__ == '__main__':
    main('python39')
