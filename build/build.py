import os
import shutil

from lk_utils import find_files

try:  # importing pyportable-installer
    # noinspection PyUnresolvedReferences
    from pyportable_installer import full_build
except ImportError:
    try:
        import sys
        
        dir_0 = input('pyportable_installer parent dir: ')
        sys.path.append(dir_0)
        dir_1 = input('pyportable_installer related venv dir: ')
        sys.path.append(f'{dir_1}/lib/site-packages')
        # noinspection PyUnresolvedReferences
        from pyportable_installer import full_build
    except Exception as e:
        raise e
    else:
        del sys


# ------------------------------------------------------------------------------

def main(full_pack: bool, **kwargs):
    """
    
    Args:
        full_pack:
        **kwargs:
            precheck: bool[True]
            add_windows_patch: optional[list[int[1, 2, 3, 4]]]
                None: do not add windows patch
                1: add windows 7 32bit
                2: add windows 7 64bit
                3: add windows 8 32bit
                4: add windows 8 64bit
            rename: bool[True]
    """
    if kwargs.get('precheck', True):
        _precheck()
    
    conf = full_build('pyproject.json')
    dist_root = conf['build']['dist_dir']
    
    # do not encrypt depsland/doctor.py
    os.remove(d := f'{dist_root}/src/depsland/doctor.py')
    shutil.copyfile('../depsland/doctor.py', d)
    
    _use_custom_setup_launcher(dist_root)
    
    _create_embed_python_manager(dist_root, full_assets=full_pack)
    
    if x := kwargs.get('add_windows_patch'):
        _copy_windows_patch(dist_root, x)
    
    if kwargs.get('rename', True):
        if full_pack:
            os.rename(dist_root, dist_root + '-win64-full')
        else:
            os.rename(dist_root, dist_root + '-win64-standard')


def _precheck():
    if not os.path.exists('./pyportable_runtime'):
        raise Exception(
            'couldn\'t find precompiled pyportable_runtime package.',
            'see `~/docs/steps-to-prebuild-pyportable-runtime-package.zh.md` '
            'for help.'
        )


def _use_custom_setup_launcher(dist_root: str):
    # replace `<dist>/setup.exe` with custom setup.bat
    os.remove(f'{dist_root}/setup.exe')
    shutil.copyfile('setup_bundle/setup_depsland.bat', f'{dist_root}/setup.bat')


def _create_embed_python_manager(dist_root, full_assets: bool):
    assets = dist_root + '/venv/lib/site-packages/embed_python_manager/assets'
    if os.path.exists(assets):
        shutil.rmtree(assets)
    
    if full_assets:
        # about 33MB
        shutil.copytree('assets/post_build/embed_python_manager/assets', assets)
    else:
        os.mkdir(f'{assets}')
        os.mkdir(f'{assets}/embed_python')
        os.mkdir(f'{assets}/embed_python/windows')
        os.mkdir(f'{assets}/pip_suits')
        os.mkdir(f'{assets}/pip_suits/python2')
        os.mkdir(f'{assets}/pip_suits/python3')
        os.mkdir(f'{assets}/tk_suits')
        os.mkdir(f'{assets}/tk_suits/python2')
        # os.mkdir(f'{assets}/tk_suits/python3')
        # add tkinter (about 5MB)
        shutil.copytree('assets/post_build/embed_python_manager/assets/tk_suits'
                        '/python3', f'{assets}/tk_suits/python3')


def _copy_windows_patch(dist_root: str, select: list):
    for number, assets_dir in {
        1: 'windows_patch/windows-7-sp1-32bit',
        2: 'windows_patch/windows-7-sp1-64bit',
        3: 'windows_patch/windows-8-32bit',
        4: 'windows_patch/windows-8-64bit',
    }.items():
        if number in select:
            for fp, fn in find_files(assets_dir, fmt='zip'):
                fp_i, fp_o = fp, f'{dist_root}/build/{assets_dir}/{fn}'
                if not os.path.exists(fp_o):
                    shutil.copyfile(fp_i, fp_o)


if __name__ == '__main__':
    main(full_pack=True, add_windows_patch=[2])
