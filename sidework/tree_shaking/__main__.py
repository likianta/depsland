from argsense import cli

from lk_utils import fs
from lk_utils import p
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


if __name__ == '__main__':
    # pox -m sidework.tree_shaking -h
    # pox -m sidework.tree_shaking dump-all-references
    #   sidework/tree_shaking/_test.py
    # pox -m sidework.tree_shaking dump-all-references
    #   depsland/__main__.py
    cli.run()
