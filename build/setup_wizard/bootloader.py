"""
note:

1. this module uses only standard libraries.
2. this module runs fast (estimated under 2 seconds)
"""
import os
import sys
import typing as t
from subprocess import call as subcall


class T:
    Name = str
    RawName = str
    Version = str


class Paths:
    root = os.path.abspath(f'{__file__}/../../../').replace('\\', '/')
    pypi = f'{root}/pypi'
    downloads = f'{root}/pypi/downloads'
    installed = f'{root}/pypi/installed'
    site_packages = f'{root}/python/Lib/site-packages'


paths = Paths()


def main() -> None:
    if _check_prerequisites():
        print('bootloader already done. launch gui now.')
        _launch_gui()
        return
    
    print(f'located project root: {paths.root}')
    # _pip_install(paths.downloads, paths.installed)
    _make_soft_links(paths.installed, paths.site_packages)
    _rebuild_pypi_index()
    _launch_gui()


def _check_prerequisites() -> bool:
    # check windows symlink permission.
    try:
        os.symlink(__file__, f'{paths.root}/test')
    except OSError:
        input('please run this script as administrator. '
              '(press enter to exit)')
        sys.exit(1)
    else:
        os.unlink(f'{paths.root}/test')
    
    # is site-packages ready
    try:
        import argsense
    except (ImportError, ModuleNotFoundError):
        return False
    else:
        return True


def _pip_install(dir_i: str, dir_o: str) -> None:
    for fn in os.listdir(dir_i):
        if fn.startswith('.'): continue
        print(f'installing: {fn}')
        name, ver = _filename_2_name_version(fn)
        d = f'{dir_o}/{name}/{ver}'
        os.makedirs(d)
        subcall([
            sys.executable, '-m', 'pip',
            'install', f'{dir_i}/{fn}',
            '-t', d,
            '--no-warn-script-location',
            '--no-deps',
            '--no-index',
        ])


def _make_soft_links(root_i: str, root_o: str) -> None:
    for name in os.listdir(root_i):
        if name.startswith(('.', '__')):
            continue
        for version in os.listdir(f'{root_i}/{name}'):
            assert not version.startswith(('.', '__'))
            for dname in os.listdir(f'{root_i}/{name}/{version}'):
                if dname.startswith(('.', '__')) or dname == 'bin':
                    continue
                path_i = f'{root_i}/{name}/{version}/{dname}'
                path_o = f'{root_o}/{dname}'
                os.symlink(
                    path_i,
                    path_o,
                    target_is_directory=os.path.isdir(path_i)
                )
            # there is only one version, we can break right now
            break


def _rebuild_pypi_index() -> None:
    from depsland import rebuild_pypi_index
    rebuild_pypi_index()


def _launch_gui() -> None:
    from build.setup_wizard.run import main
    main(False, False)


# -----------------------------------------------------------------------------

def _filename_2_name_version(filename: str) -> t.Tuple[T.Name, T.Version]:
    """
    examples:
        'PyYAML-6.0-cp310-cp310-macosx_10_9_x86_64.whl' -> ('pyyaml', '6.0')
        'lk-logger-4.0.7.tar.gz' -> ('lk_logger', '4.0.7')
        'aliyun-python-sdk-2.2.0.zip' -> ('aliyun_python_sdk', '2.2.0')
    """
    for ext in ('.whl', '.tar.gz', '.zip'):
        if filename.endswith(ext):
            filename = filename.removesuffix(ext)
            break
    else:
        raise ValueError(filename)
    # assert ext
    if ext == '.whl':
        a, b, _ = filename.split('-', 2)
    else:
        a, b = filename.rsplit('-', 1)
    a = _normalize_name(a)
    return a, b


def _normalize_name(raw_name: T.RawName) -> T.Name:
    """
    e.g. 'lk-logger' -> 'lk_logger'
         'PySide6' -> 'pyside6'
    """
    return raw_name.strip().lower().replace('-', '_')


if __name__ == '__main__':
    main()
