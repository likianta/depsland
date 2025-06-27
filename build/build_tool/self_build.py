import os
from os.path import exists

from lk_utils import fs

from depsland import paths
from depsland.manifest import dump_manifest
from depsland.manifest import load_manifest


def build_dist(
    version: str,
    oss_scheme: str,
    pypi_scheme: str = 'blank',
    _add_python_sdk: bool = True,
) -> None:
    """
    generate `dist/standalone/depsland-<version>`.
    
    args:
        oss_scheme: 'aliyun' or 'local'
            - 'aliyun': you need to prepare a file named -
            'config/depsland_for_dev.yaml', which contains aliyun oss access -
            key and secret key.
    kwargs:
        pypi_scheme (-p): 'full', 'blank'
            - full: link `<proj>/pypi` to `<dist>/pypi`.
            - blank: copy `<proj>/chore/pypi_blank` to `<dist>/pypi`.
            what's the difference?
                'full' is used for local test.
                'blank' is used for production release, it has a minified -
                size.
                if you want to partially release, or try to package a minimal -
                version, use `pypi_scheme='blank'` with `_add_python_sdk=False`.
    """
    if fs.exists('depsland/.project'):
        raise Exception('please remove "depsland/.project" to continue.')
    
    # checks
    if oss_scheme == 'aliyun':
        assert exists(os.getenv('DEPSLAND_CONFIG_ROOT'))
    
    root_i = paths.project.root
    root_o = (
        '{dist}/standalone/depsland-{version}-windows'
        .format(dist=paths.project.dist, version=version)
    )
    # ^ related doc: `wiki/design-tkinking/why-does-dist-standalone-directory
    #   -like-this.md`
    assert not exists(root_o)
    os.mkdir(root_o)
    
    # -------------------------------------------------------------------------
    
    # make empty dirs
    # os.mkdir(f'{root_o}/apps')
    # os.mkdir(f'{root_o}/apps/.bin')
    # os.mkdir(f'{root_o}/apps/.venv')
    os.mkdir(f'{root_o}/build')
    os.mkdir(f'{root_o}/chore')
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
    
    # copy files and folders
    fs.make_link(
        f'{root_i}/build/exe',
        f'{root_o}/build/exe',
    )
    # fs.copy_file(
    #     f'{root_i}/build/exe/depsland-cli.exe',
    #     f'{root_o}/apps/.bin/depsland.exe',
    # )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui.exe',
        f'{root_o}/Depsland.exe',
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui-debug.exe',
        f'{root_o}/Depsland (Debug).exe',
    )
    fs.make_link(
        f'{root_i}/build/icon',
        f'{root_o}/build/icon',
    )
    fs.make_link(
        f'{root_i}/chore/pypi_blank',
        f'{root_o}/chore/pypi_blank',
    )
    fs.make_link(
        f'{root_i}/depsland',
        f'{root_o}/depsland',
    )
    # fs.copy_tree(
    #     f'{root_i}/sidework',
    #     f'{root_o}/sidework',
    # )
    # fs.copy_file(
    #     f'{root_i}/.depsland_project.json',
    #     f'{root_o}/.depsland_project.json',
    # )
    
    fs.dump(
        {'project_mode': 'production', 'depsland_version': version},
        f'{root_o}/.depsland_project.json'
    )
    
    if oss_scheme == 'aliyun':
        # assert exists(custom := os.getenv('DEPSLAND_CONFIG_ROOT'))
        custom = os.getenv('DEPSLAND_CONFIG_ROOT')
        assert (
            fs.load(f'{custom}/depsland.yaml')
            ['oss']['server'] == 'aliyun'
        )
        fs.copy_file(
            f'{custom}/depsland.yaml',
            f'{root_o}/config/depsland.yaml',
        )
    else:
        assert (
            fs.load(f'{root_i}/config/depsland.yaml')
            ['oss']['server'] == 'local'
        )
        fs.copy_file(
            f'{root_i}/config/depsland.yaml',
            f'{root_o}/config/depsland.yaml',
        )
    
    if pypi_scheme == 'full':
        fs.make_link(f'{root_i}/apps', f'{root_o}/apps')
        fs.make_link(f'{root_i}/pypi', f'{root_o}/pypi')
    else:  # 'blank'
        os.mkdir(f'{root_o}/apps')
        os.mkdir(f'{root_o}/apps/.bin')
        os.mkdir(f'{root_o}/apps/.venv')
        fs.copy_file(
            f'{root_i}/build/exe/depsland-cli.exe',
            f'{root_o}/apps/.bin/depsland.exe',
        )
        fs.copy_tree(f'{root_i}/chore/pypi_blank', f'{root_o}/pypi')
    
    if _add_python_sdk:
        fs.make_link(
            f'{root_i}/chore/site_packages',
            f'{root_o}/chore/site_packages',
        )
        fs.make_link(
            f'{root_i}/python',
            f'{root_o}/python',
        )
    
    # -------------------------------------------------------------------------
    
    # dump manifest
    dump_manifest(
        load_manifest(f'{root_i}/manifest.json'),
        f'{root_o}/manifest.pkl',
    )
    
    print(':t', 'see result at ' + fs.relpath(root_o))
