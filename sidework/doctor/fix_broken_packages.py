from depsland import paths
from depsland import pypi
from depsland.venv.target_venv.indexer import analyze_records
from lk_utils import fs, p
from argsense import cli


@cli.cmd()
def find() -> None:
    broken_packages = []
    for id, (p0, p1) in pypi.index.id_2_paths.items():
        if p0.endswith('.zip'):
            record_file = '{}/{}/{}.dist-info/RECORD'.format(
                paths.pypi.root, p1, id
            )
            if not fs.exists(record_file):
                print('record not found', id, record_file)
                continue
            relpath_files = analyze_records(record_file)
            temp = set()
            for x in relpath_files:
                if x.startswith('../'):
                    continue
                if '/' in x:
                    x = x.rsplit('/', 1)[0]
                    if '/.' in x:
                        temp.add(x)
            if temp:
                print('package broken', id, temp, ':lv4i')
                broken_packages.append(id)
    if broken_packages:
        fs.dump(broken_packages, p('_broken_packages.yaml'))


@cli.cmd()
def remove() -> None:
    broken_packages = fs.load(p('_broken_packages.yaml'))
    
    for id in broken_packages:
        p0, p1 = pypi.index.id_2_paths[id]
        fs.remove_file(p0)
        fs.remove_tree(p1)
    
    oss_pypi = fs.load(paths.oss.pypi)
    for id in broken_packages:
        p0, p1 = pypi.index.id_2_paths[id]
        if (x := fs.basename(p0)) in oss_pypi:
            oss_pypi.remove(x)
    fs.dump(oss_pypi, paths.oss.pypi)
    
    for id in broken_packages:
        pypi.index.id_2_paths.pop(id)
        name, ver = id.split('-')
        pypi.index.name_2_vers[name].remove(ver)
    fs.dump(pypi.index.id_2_paths, paths.pypi.id_2_paths)
    fs.dump(pypi.index.name_2_vers, paths.pypi.name_2_vers)
    
    # fs.remove(p('_broken_packages.yaml'))
    
    # next: better to manually recheck the broken packages.


if __name__ == '__main__':
    # pox sidework/doctor/fix_broken_packages.py find
    # pox sidework/doctor/fix_broken_packages.py remove
    cli.run()
