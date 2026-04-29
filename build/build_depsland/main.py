import os
from argsense import cli
from depsland import paths
from depsland.api.dev_api import build_project
from depsland.api.dev_api.build_project import bump_version as _bump_version
from lk_utils import fs
from lk_utils import run_cmd_args


@cli
def bump_version(new_ver: str = '') -> None:
    _bump_version('build/build_depsland/build_project.json', new_ver)


@cli
def main(
    new_version: str = '',
    compress: bool = False,
    upload_to_oss: bool = False,
) -> None:
    """
    params:
        new_version (-v):
        compress (-z):
        upload_to_oss (-u):
    """
    _, new_ver = build_project(
        file='build/build_depsland/build_project.json',
        new_version=new_version,
        minify_deps=2,
        publish=0,
    )

    dist_dir = make_dist(new_ver, 'aliyun')
    if compress:
        dist_file = fs.zip_dir(
            dist_dir,
            dist_dir + '.7z',
            compression_level='maximum',
            progress=True,
        )
        print(
            ':t',
            'compressed: {} ({})'.format(
                fs.relpath(dist_file), fs.filesize(dist_file, str)
            ),
        )

        if upload_to_oss:
            print(
                """
                1. copy or move the ".7z" file to `resources` folder.
                2. upload the ".7z" file to `oss:/likianta-public-share/depsland
                -resources/depsland.7z`
                    command: `ossutil cp resources/depsland.7z 
                    oss://likianta-public-share/depsland-resources
                    /depsland.7z -f`
                3. update code at `depsland/gui/setup_wizard/depsland_installer
                _online.py:State.depsland_version`
                4. check code at `sidework/mini_launcher/app_launcher.v
                :check_version_of_installed_depsland`
                """
            )
            # a = fs.basename(dist_file)
            a = 'depsland.7z'
            b = 'resources/{}'.format(a)
            fs.move(dist_file, b, True)
            # fmt: off
            run_cmd_args(
                (
                    'ossutil', 'cp', b,
                    'oss://likianta-public-share/depsland-resources/{}'
                    .format(a), '-f',
                ),
                verbose=True,
            )
            # fmt: on


@cli
def make_dist(
    version: str,
    oss_scheme: str,
    pypi_scheme: str = 'blank',
    _add_python_sdk: bool = True,
) -> str:
    """
    generate `/dist/standalone/depsland-<version>`.

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
    if fs.exist('depsland/.project'):
        raise Exception('please remove "depsland/.project" to continue.')

    # checks
    if oss_scheme == 'aliyun':
        # noinspection PyTypeChecker
        assert fs.exist(os.environ['DEPSLAND_CONFIG_ROOT'])

    root_i = paths.project.root
    root_o = '{dist}/standalone/depsland-{version}'.format(
        dist=paths.project.dist, version=version
    )
    # ^ related doc: `wiki/design-tkinking/why-does-dist-standalone-directory
    #   -like-this.md`
    assert not fs.exist(root_o)
    os.mkdir(root_o)

    # -------------------------------------------------------------------------

    # make empty dirs
    # os.mkdir(f'{root_o}/apps')
    # os.mkdir(f'{root_o}/apps/.bin')
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
    os.mkdir(f'{root_o}/temp/temp_project')

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
    fs.make_link(  # TEST
        f'{root_i}/chore/setup_wizard_logo.png',
        f'{root_o}/chore/setup_wizard_logo.png',
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
        f'{root_o}/.depsland_project.json',
    )

    if oss_scheme == 'aliyun':
        # assert exists(custom := os.getenv('DEPSLAND_CONFIG_ROOT'))
        custom = os.getenv('DEPSLAND_CONFIG_ROOT')
        assert fs.load(f'{custom}/depsland.yaml')['oss']['server'] == 'aliyun'
        fs.copy_file(
            f'{custom}/depsland.yaml',
            f'{root_o}/config/depsland.yaml',
        )
    else:
        assert (
            fs.load(f'{root_i}/config/depsland.yaml')['oss']['server']
            == 'local'
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
        fs.copy_file(
            f'{root_i}/build/exe/depsland-cli.exe',
            f'{root_o}/apps/.bin/depsland.exe',
        )
        fs.copy_tree(f'{root_i}/chore/pypi_blank', f'{root_o}/pypi')

    if _add_python_sdk:
        fs.make_link(f'{root_i}/chore/minideps', f'{root_o}/chore/minideps')
        fs.make_link(f'{root_i}/python', f'{root_o}/python')

    _make_disguised_packages('chore/minideps')

    print(':t', 'created distribution: {}'.format(fs.relpath(root_o)))
    return root_o


def _make_disguised_packages(site_packages_dir: str) -> None:
    """
    doc: /chore/disguised_packages/readme.md
    """
    for pkg_name in ('matplotlib', 'numpy', 'pandas'):
        dir_o = f'{site_packages_dir}/{pkg_name}'
        if fs.exist(dir_o):
            if fs.islink(dir_o):
                print('{} linked'.format(pkg_name), ':v')
                continue
            else:
                raise Exception(dir_o)
        else:
            dir_i = f'chore/disguised_packages/{pkg_name}'
            fs.make_link(dir_i, dir_o)


if __name__ == '__main__':
    # prerequisites:
    #   1. nushell: `$env.DEPSLAND_CONFIG_ROOT = 'test/_config'`
    #   2. make sure poetry.lock is latest.
    # pox build/build_depsland/main.py main -z -u
    cli.run()
