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
    dir_o: str
) -> None:
    """
    params:
        dir_o (-o):
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
    relpath_files_i = set()
    refs = index_all_package_references(dir_i)
    for pkg_name, (dir_name, dir_path) in refs:
        if pkg_name in all_required_pkg_names:
            record_file = '{}/RECORD'.format(dir_path)
            relpaths = analyze_records(record_file)
            relpath_files_i.update(relpaths)
    
    if not fs.exist(dir_o):
        fs.make_dir(dir_o)
    init_target_tree(dir_o, relpath_files_i)
    for relpath in sorted(relpath_files_i):
        file_i = '{}/{}'.format(dir_i, relpath)
        file_o = '{}/{}'.format(dir_o, relpath)
        fs.make_link(file_i, file_o)


if __name__ == '__main__':
    # pox sidework/export_deps.py analyze <poetry_file>
    cli.run()
