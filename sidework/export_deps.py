from argsense import cli
from depsland.depsolver import analyze_dependency_tree
from depsland.venv import get_library_root
from depsland.venv.target_venv.indexer import analyze_records
from depsland.venv.target_venv.indexer import index_all_package_references
from depsland.utils import init_target_tree
from lk_utils import fs


@cli
def analyze(
    poetry_file: str,
    *wanted_package_names: str,
    file_o: str = None
) -> None:
    """
    params:
        file_o (-o):
    """
    assert wanted_package_names
    tree = analyze_dependency_tree(
        poetry_file,
        excluded_project_name=fs.dirname(poetry_file).replace('-', '_')
    )
    
    expected_packages = {}  # {pkg_id: [dep_id, ...], ...}
    for name in wanted_package_names:
        ver, deps = tree[name]
        expected_packages['{}-{}'.format(name, ver)] = sorted(
            '{}-{}'.format(dep_name, dep_ver)
            for dep_name, dep_ver in deps
        )
    assert expected_packages
    print(expected_packages, ':lv2')
    
    if file_o:
        fs.dump(expected_packages, file_o)


@cli
def export(
    poetry_file: str,
    *wanted_package_names: str,
    dir_o: str,
    by_packages: bool = True,
    compress: bool = True,
) -> None:
    """
    params:
        dir_o (-o):
        by_packages (-p):
            if true, the generated structure would be:
                <dir_o>
                |= ipython-9.6.0
                   |= bin
                      |- ipython.1
                      |- ipython.exe
                      |- ipython3.exe
                   |= IPython
                   |= ipython-9.6.0.dist-info
                |= pyserial-3.5
                   |= bin
                      |- pyserial-miniterm.exe
                      |- pyserial-ports.exe
                   |= pyserial-3.5.dist-info
                   |= serial
                |= ...
            else it would be:
                <dir_o>
                |= bin
                   |- ipython.1
                   |- ipython.exe
                   |- ipython3.exe
                   |- pyserial-miniterm.exe
                   |- pyserial-ports.exe
                |= IPython
                |= ipython-9.6.0.dist-info
                |= pyserial-3.5.dist-info
                |= serial
        compress: if `by_packages` enabled, would compress each dir to zip file.
    """
    assert wanted_package_names
    tree = analyze_dependency_tree(
        poetry_file,
        excluded_project_name=fs.dirname(poetry_file).replace('-', '_')
    )
    all_required_pkg_names = set()
    for name in wanted_package_names:
        _, deps = tree[name]
        all_required_pkg_names.add(name)
        all_required_pkg_names.update(x for x, _ in deps)
    del wanted_package_names
    
    dir_i = get_library_root(fs.parent(poetry_file))
    pkg_name_2_relpaths = {}
    refs = index_all_package_references(dir_i)
    for pkg_name, (dir_name, dir_path) in refs:
        if pkg_name in all_required_pkg_names:
            record_file = '{}/RECORD'.format(dir_path)
            relpaths = analyze_records(record_file)
            pkg_name_2_relpaths[pkg_name] = tuple(relpaths)
    
    def get_relpath_dirs(relpath_files):
        out = set()
        for f in relpath_files:
            f = suppress_super_path(f)
            assert '/' in f
            out.add(f.rsplit('/', 1)[0])
        return sorted(out)
    
    def suppress_super_path(path: str) -> str:
        if path.startswith('../'):
            assert path.startswith('../../Scripts/')
            return path.replace('../../Scripts/', 'bin/')
        else:
            return path
    
    if not fs.exist(dir_o):
        fs.make_dir(dir_o)
    if by_packages:
        for name, relpaths in pkg_name_2_relpaths.items():
            if not fs.exist(pkg_dir := '{}/{}'.format(dir_o, name)):
                fs.make_dir(pkg_dir)
                init_target_tree(pkg_dir, get_relpath_dirs(relpaths))
                for relpath in sorted(relpaths):
                    file_i = '{}/{}'.format(dir_i, relpath)
                    file_o = '{}/{}'.format(
                        pkg_dir, suppress_super_path(relpath)
                    )
                    fs.make_link(file_i, file_o)
            if compress and not fs.exist(pkg_zip := '{}.zip'.format(pkg_dir)):
                fs.zip_dir(pkg_dir, pkg_zip)
    else:
        all_relpath_files_i = set()
        for relpaths in pkg_name_2_relpaths.values():
            all_relpath_files_i.update(relpaths)
        init_target_tree(dir_o, get_relpath_dirs(all_relpath_files_i))
        for relpath in sorted(all_relpath_files_i):
            file_i = '{}/{}'.format(dir_i, relpath)
            file_o = '{}/{}'.format(dir_o, suppress_super_path(relpath))
            fs.make_link(file_i, file_o)


if __name__ == '__main__':
    # pox sidework/export_deps.py analyze <poetry_file>
    # pox sidework/export_deps.py export -h
    # pox sidework/export_deps.py export <poetry_file> pyserial modbus_tk -o ...
    cli.run()
