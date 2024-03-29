"""
py build/build.py full-build aliyun
py build/build.py full-build local
"""
if 1:
    import sys
    from lk_utils import xpath
    sys.path.insert(0, xpath('..', True))

import os
from os.path import exists

from argsense import cli
from lk_utils import fs
from lk_utils import loads

from depsland import __version__
from depsland import bat_2_exe as _b2e
from depsland import paths
from depsland.manifest import dump_manifest
from depsland.manifest import load_manifest
from depsland.utils import ziptool

print(':v2', f'depsland version: {__version__}')


@cli.cmd()
def full_build(
    oss_scheme: str, pypi_scheme='full', _add_python_path=True
) -> None:
    """
    generate `dist/depsland-setup-<version>` folder.
    
    args:
        oss_scheme: 'aliyun' or 'local'
            aliyun: you need to prepare a file named -
            'config/depsland_for_dev.yaml', which contains aliyun oss access -
            & secret keys.
    kwargs:
        pypi_scheme (-p): 'full', 'least', 'none'
            full: link `<proj>/pypi_self` to `<dist>/pypi`.
            least: init `<dist>/pypi`, and link `<proj>/pypi_self/downloads` -
                to `<dist>/pypi/downloads`.
            none: just init `<dist>/pypi`.
    """
    root_i = paths.project.root
    root_o = '{dist}/depsland-setup-{version}'.format(
        dist=paths.project.dist, version=__version__
    )
    assert not exists(root_o)
    os.mkdir(root_o)
    
    # -------------------------------------------------------------------------
    
    # make empty dirs
    os.mkdir(f'{root_o}/apps')
    os.mkdir(f'{root_o}/apps/.bin')
    os.mkdir(f'{root_o}/apps/.venv')
    os.mkdir(f'{root_o}/build')
    os.mkdir(f'{root_o}/build/exe')
    os.mkdir(f'{root_o}/config')
    # os.mkdir(f'{root_o}/depsland')
    os.mkdir(f'{root_o}/dist')
    os.mkdir(f'{root_o}/docs')
    os.mkdir(f'{root_o}/oss')
    os.mkdir(f'{root_o}/oss/apps')
    os.mkdir(f'{root_o}/oss/test')
    # os.mkdir(f'{root_o}/pypi')
    # os.mkdir(f'{root_o}/python')
    # os.mkdir(f'{root_o}/sidework')
    os.mkdir(f'{root_o}/temp')
    os.mkdir(f'{root_o}/temp/.self_upgrade')
    os.mkdir(f'{root_o}/temp/.unittests')
    
    # -------------------------------------------------------------------------
    
    # copy files
    fs.copy_file(
        f'{root_i}/build/exe/depsland.exe',
        f'{root_o}/build/exe/depsland.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-sui.exe',
        f'{root_o}/build/exe/depsland-sui.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-suw.exe',
        f'{root_o}/build/exe/depsland-suw.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/desktop.exe',
        f'{root_o}/build/exe/desktop.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/launcher.ico',
        f'{root_o}/build/exe/launcher.ico',
    )
    fs.copy_file(
        f'{root_i}/build/exe/setup.exe',
        f'{root_o}/setup.exe',
    )
    fs.copy_tree(
        f'{root_i}/build/setup_wizard',
        f'{root_o}/build/setup_wizard',
    )
    fs.copy_file(
        f'{root_i}/build/depsland_setup.py',
        f'{root_o}/build/depsland_setup.py',
    )
    fs.copy_tree(
        f'{root_i}/depsland',
        f'{root_o}/depsland',
    )
    fs.copy_tree(
        f'{root_i}/sidework',
        f'{root_o}/sidework',
    )
    fs.copy_file(
        f'{root_i}/.depsland_project',
        f'{root_o}/.depsland_project',
    )
    
    if oss_scheme == 'aliyun':
        assert exists(custom := os.getenv('DEPSLAND_CONFIG_ROOT'))
        assert (
            loads(f'{custom}/depsland.yaml')
            ['oss']['server'] == 'aliyun'
        )
        fs.copy_file(
            f'{custom}/depsland.yaml',
            f'{root_o}/config/depsland.yaml',
        )
    else:
        assert (
            loads(f'{root_i}/config/depsland.yaml')
            ['oss']['server'] == 'local'
        )
        fs.copy_file(
            f'{root_i}/config/depsland.yaml',
            f'{root_o}/config/depsland.yaml',
        )
    
    if _add_python_path:
        if pypi_scheme == 'full':
            fs.make_link(
                f'{root_i}/python',
                f'{root_o}/python',
            )
        else:
            assert exists(f'{root_i}/tests/pure_python_standalone')
            fs.make_link(
                f'{root_i}/tests/pure_python_standalone',
                f'{root_o}/python',
            )
    
    if pypi_scheme == 'full':
        fs.make_link(f'{root_i}/pypi_self', f'{root_o}/pypi')
    elif pypi_scheme == 'least':
        assert exists(f'{root_i}/tests/pure_pypi_index')
        fs.copy_tree(
            f'{root_i}/tests/pure_pypi_index',
            f'{root_o}/pypi',
        )
        fs.remove_tree(f'{root_o}/pypi/downloads')
        fs.make_link(
            f'{root_i}/pypi_self/downloads',
            f'{root_o}/pypi/downloads',
        )
        fs.remove_tree(f'{root_o}/pypi/installed')
        fs.make_link(
            f'{root_i}/pypi_self/installed',
            f'{root_o}/pypi/installed',
        )
    else:
        assert exists(f'{root_i}/tests/pure_pypi_index')
        fs.copy_tree(
            f'{root_i}/tests/pure_pypi_index',
            f'{root_o}/pypi',
        )
    
    # -------------------------------------------------------------------------
    
    # dump manifest
    dump_manifest(
        load_manifest(f'{root_i}/manifest.json'),
        f'{root_o}/manifest.pkl',
    )
    
    # post check
    if pypi_scheme == 'least':
        print('overwrite setup.exe')
        fs.copy_file(
            f'{root_i}/build/exe/setup2.exe',
            f'{root_o}/setup.exe',
            overwrite=True,
        )
    if pypi_scheme in ('least', 'none'):
        print(
            'note: you need to manually remove `python/lib/site-packages/'
            '<symlinked_names>` before publishing this dist',
            ':v3',
        )
    
    print(':t', 'see result at ' + fs.relpath(root_o))


@cli.cmd()
def bat_2_exe(file_i: str, show_console=True, uac_admin=False):  # FIXME
    """
    args:
        file_i: the file is ".bat" file, which is under ~/build/exe folder.
    
    kwargs:
        show_console (-c):
        uac_admin (-u):
    """
    _b2e(
        file_i,
        icon=xpath('exe/launcher.ico'),
        show_console=show_console,
        uac_admin=uac_admin,
    )


@cli.cmd()
def build_all_launchers():  # FIXME
    for f in fs.find_files(xpath('exe'), '.bat'):
        print(':i', f.name)
        _b2e(f.path, icon=xpath('exe/launcher.ico'))


@cli.cmd()
def compress_to_zip():
    dir_i = '{}/{}'.format(paths.project.dist, f'depsland-{__version__}')
    file_o = '{}/{}'.format(paths.project.dist, f'depsland-{__version__}.zip')
    ziptool.compress_dir(dir_i, file_o, overwrite=True)
    print(':t', 'see result at', fs.relpath(file_o))


if __name__ == '__main__':
    cli.run()
