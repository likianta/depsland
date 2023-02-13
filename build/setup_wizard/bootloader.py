"""
this module uses only standard libraries.
"""
import os
import sys
import typing as t
from collections import defaultdict
from subprocess import call as subcall


class T:
    AbsPath = str
    Name = str
    NameId = str
    RawName = str
    RelPath = str
    Version = str
    
    NameIds = t.Sequence[NameId]
    Ownership = t.Dict[RelPath, NameId]


class Paths:
    root = os.path.abspath(f'{__file__}/../../../').replace('\\', '/')
    pypi = f'{root}/pypi'
    downloads = f'{root}/pypi/downloads'
    installed = f'{root}/pypi/installed'
    site_packages = f'{root}/python/Lib/site-packages'


paths = Paths()


def main() -> None:
    print(f'located project root: {paths.root}')
    _check_permission()
    _pip_install(paths.downloads, paths.installed)
    _make_soft_links(paths.site_packages)


def _check_permission() -> None:
    # check windows symlink permission.
    try:
        os.symlink(__file__, f'{paths.root}/test')
    except OSError:
        input('please run this script as administrator. '
              '(press enter to exit)')
        sys.exit(1)
    else:
        os.remove(f'{paths.root}/test')


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


def _make_soft_links(dir_o: str) -> None:
    dirname_2_name_ids = defaultdict(list)
    name_ids = _collect_name_ids()
    for nid in name_ids:
        dir_ = _name_id_2_path(nid)
        for dname in os.listdir(dir_):
            if dname == '__pycache__':
                continue
            dirname_2_name_ids[dname].append(nid)
    
    ownership: T.Ownership = {}
    for dname, name_ids in dirname_2_name_ids.items():
        if len(name_ids) == 1:
            ownership[dname] = name_ids[0]
        else:
            ownership.update(_distribute_ownerships(dname, name_ids))
    
    _init_dirs(dir_o, ownership.keys())
    for relpath, name_id in sorted(
            ownership.items(), key=lambda x: x[1]  # sort by name_id.
    ):
        # print(name_id, relpath, ':vs')
        os.symlink(
            src := '{}/{}'.format(_name_id_2_path(name_id), relpath),
            '{}/{}'.format(dir_o, relpath),
            target_is_directory=os.path.isdir(src)
        )


def _launch_gui() -> None:
    from build.setup_wizard.run import main
    main(False, False)


# -----------------------------------------------------------------------------

def _collect_name_ids() -> t.Iterator[T.NameId]:
    for dn0 in os.listdir(paths.installed):
        if dn0.startswith('.'):
            continue
        for dn1 in os.listdir(f'{paths.installed}/{dn0}'):
            if dn1.startswith('.'):
                continue
            yield f'{dn0}-{dn1}'


def _distribute_ownerships(
        relpath: T.RelPath, candidates: T.NameIds
) -> T.Ownership:
    """
    docs: docs/dev-notes/merge-links-algorithm.md
    """
    file_asset_2_name_ids = defaultdict(list)
    dir_asset_2_name_ids = defaultdict(list)
    relpath_2_name_id = {}
    
    for nid in candidates:
        dir_ = '{}/{}'.format(_name_id_2_path(nid), relpath)
        for asset in os.listdir(dir_):
            if asset == '__pycache__':
                continue
            if os.path.isdir(f'{dir_}/{asset}'):
                dir_asset_2_name_ids[asset].append(nid)
            else:
                file_asset_2_name_ids[asset].append(nid)
    
    for name, name_ids in file_asset_2_name_ids.items():
        if len(name_ids) > 1:
            print('multiple owners for a file (will choose the first one)',
                  name, name_ids, ':v3')
        relpath_2_name_id[f'{relpath}/{name}'] = name_ids[0]
    
    for name, name_ids in dir_asset_2_name_ids.items():
        if len(name_ids) > 1:
            print('[yellow dim]multiple owners for a dir (will merge them)[/]',
                  name, name_ids, ':rv')
            relpath_2_name_id.update(
                _distribute_ownerships(f'{relpath}/{name}', name_ids)
            )
        else:
            relpath_2_name_id[f'{relpath}/{name}'] = name_ids[0]
    
    return relpath_2_name_id


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


def _init_dirs(root_dir: T.AbsPath, paths: t.Iterable[T.RelPath]) -> None:
    dirs_to_be_created = set(os.path.dirname(x) for x in paths)
    dirs_to_be_created.remove('.')
    for relpath in sorted(dirs_to_be_created):
        abspath = f'{root_dir}/{relpath}'
        os.makedirs(abspath)


def _name_id_2_path(name_id: T.NameId) -> T.AbsPath:
    name, ver = name_id.split('-', 1)
    return '{}/{}/{}'.format(paths.installed, name, ver)


def _normalize_name(raw_name: T.RawName) -> T.Name:
    """
    e.g. 'lk-logger' -> 'lk_logger'
         'PySide6' -> 'pyside6'
    """
    return raw_name.strip().lower().replace('-', '_')
