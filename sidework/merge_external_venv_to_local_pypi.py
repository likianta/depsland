import typing as t
from os.path import isfile

from argsense import cli

from depsland import paths
from depsland import pypi
from depsland.depsolver import resolve_dependencies
from depsland.utils import init_target_tree
from depsland.utils import ziptool
from depsland.venv.target_venv import get_library_root
from lk_utils import fs


@cli.cmd()
def main(external_proj_dir: str) -> None:
    lib_root = get_library_root(external_proj_dir)
    pkgs = resolve_dependencies('poetry.lock', external_proj_dir)
    for info in pkgs.values():
        id = info['id']
        if id not in pypi:
            print(':it', id)
            _compress_dependency(lib_root, id, info['files'])


def _compress_dependency(
    lib_root: str, package_id: str, relpaths: t.Tuple[str, ...]
) -> str:
    path0 = '{}/{}.zip'.format(paths.pypi.downloads, package_id)
    path1 = '{}/{}/{}'.format(paths.pypi.installed, *package_id.split('-'))
    if fs.exists(path0):
        assert fs.exists(path1)
        return path0
    
    reldirs = set()
    for p in relpaths:
        if p.startswith('../'):
            reldirs.add('bin')
        else:
            if '/' in p:
                reldirs.add(p.rsplit('/', 1)[0])
    init_target_tree(path1, reldirs)
    
    # copy files
    for p in relpaths:
        if p.startswith('../'):
            file_i = fs.normpath('{}/{}'.format(lib_root, p))
            file_o = '{}/bin/{}'.format(path1, fs.basename(p))
        else:
            file_i = '{}/{}'.format(lib_root, p)
            file_o = '{}/{}'.format(path1, p)
        if isfile(file_i):
            fs.copy_file(file_i, file_o)
        else:
            print(':v3', 'not a valid file', file_i)
    
    ziptool.compress_dir(path1, path0, True)
    pypi.index.update_index(package_id, path0, path1)
    return path0


if __name__ == '__main__':
    # pox sidework/merge_external_venv_to_local_pypi.py .
    #   next: pox build/init.py make-site-packages --remove-exists
    # pox sidework/merge_external_venv_to_local_pypi.py <third_project>
    cli.run(main)
