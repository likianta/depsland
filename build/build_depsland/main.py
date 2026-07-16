import os

from argsense import cli
from lk_utils import fs
from lk_utils import run_cmd_args
from neoprint import print

from depsland import paths
from depsland.api import dev_api


@cli
def bump_version(new_ver: str = '') -> None:
    dev_api.bump_version_inplaces(fs.here('build_project.json'), new_ver)


@cli
def main(
    new_version: str = '',
    compress: bool = False,
    upload_to_oss: bool = False,
    pypi_scheme: str = 'blank',
) -> None:
    """
    params:
        new_version (-v):
        compress (-c):
        upload_to_oss (-u):
        pypi_scheme (-p): 'full' or 'blank'
    """
    _, new_ver = dev_api.build_project(
        file=fs.here('build_project.json'),
        image_key='src_max',
        new_version=new_version,
        publish=0,
    )

    dist_dir = make_dist(new_ver, 'aliyun', pypi_scheme)
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
            fs.make_link(dist_file, b, True)
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
    if oss_scheme == 'aliyun':
        assert fs.exist(os.environ['DEPSLAND_CONFIG_ROOT'])

    root_i = paths.project.root
    root_o = '{}/standalone/depsland-{}'.format(paths.project.dist, version)
    assert not fs.exist(root_o)
    os.mkdir(root_o)

    # --------------------------------------------------------------------------
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

    # --------------------------------------------------------------------------
    # copy files and folders

    fs.make_link(f'{root_i}/build/exe', f'{root_o}/build/exe')
    # fs.copy_file(
    #     f'{root_i}/build/exe/depsland-cli.exe',
    #     f'{root_o}/apps/.bin/depsland.exe',
    # )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui.exe', f'{root_o}/Depsland.exe'
    )
    fs.copy_file(
        f'{root_i}/build/exe/depsland-gui-debug.exe',
        f'{root_o}/Depsland (Debug).exe',
    )
    fs.make_link(f'{root_i}/build/icon', f'{root_o}/build/icon')
    fs.make_link(f'{root_i}/chore/pypi_blank', f'{root_o}/chore/pypi_blank')
    fs.make_link(  # TEST
        f'{root_i}/chore/setup_wizard_logo.png',
        f'{root_o}/chore/setup_wizard_logo.png',
    )
    fs.make_link(f'{root_i}/depsland', f'{root_o}/depsland')
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
            f'{custom}/depsland.yaml', f'{root_o}/config/depsland.yaml'
        )
    else:
        assert (
            fs.load(f'{root_i}/config/depsland.yaml')['oss']['server']
            == 'local'
        )
        fs.copy_file(
            f'{root_i}/config/depsland.yaml', f'{root_o}/config/depsland.yaml'
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
        os.mkdir(f'{root_o}/chore/minideps')
        for x in os.listdir(f'{root_i}/.depsland/mini_deps'):
            if x in ('matplotlib', 'numpy', 'pandas'):
                # see @chore/disguised_packages/readme.md
                fs.make_link(
                    f'{root_i}/chore/disguised_packages/{x}',
                    f'{root_o}/chore/minideps/{x}',
                )
            else:
                fs.make_link(
                    f'{root_i}/.depsland/mini_deps/{x}',
                    f'{root_o}/chore/minideps/{x}',
                )
        fs.make_link(f'{root_i}/python', f'{root_o}/python')

    print(':t', 'created distribution: {}'.format(fs.relpath(root_o)))
    return root_o


if __name__ == '__main__':
    # prerequisites:
    #   1. nushell: `$env.DEPSLAND_CONFIG_ROOT = 'test/_config'`
    #   2. make sure uv.lock latest.
    # pox build/build_depsland/main.py main -c -u
    cli.run()
