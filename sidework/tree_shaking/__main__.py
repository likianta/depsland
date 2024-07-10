from argsense import cli

from lk_utils import fs
from lk_utils import p
from .build import make_tree
from .check import check_on_lk_utils
from .finder import find_all_references


@cli.cmd()
def dump_all_references(entrances: str) -> None:
    d0 = find_all_references(*entrances.split(",,"))
    d1 = {}
    print(':i0s')
    for module in sorted(d0.keys()):
        print(module, ":iv2s")
        d1[module] = d0[module]
    fs.dump(d1, p("_references.yaml"))
    print(
        ":tv2",
        'done. dumped {} items. see result at "_references.yaml"'
        .format(len(d1))
    )


cli.add_cmd(check_on_lk_utils, 'check')
cli.add_cmd(make_tree)

if __name__ == '__main__':
    # pox -m sidework.tree_shaking -h
    # pox -m sidework.tree_shaking dump-all-references
    #   sidework/tree_shaking/_test.py
    # pox -m sidework.tree_shaking dump-all-references
    #   depsland/__main__.py
    #   prepare: make sure `chore/site_packages` latest:
    #       pox sidework/merge_external_venv_to_local_pypi.py .
    #       pox build/init.py make-site-packages --remove-exists
    # pox -m sidework.tree_shaking check
    # pox -m sidework.tree_shaking make-tree <output_dir>
    cli.run()
