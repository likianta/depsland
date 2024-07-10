from argsense import cli

from lk_utils import fs
from depsland.utils.fs import get_content_hash
from . import finder
from .build import make_tree
from .check import check_on_lk_utils


@cli.cmd()
def dump_all_imports(script: str, base_name_out: str = None) -> None:
    script = fs.abspath(script)
    result_file = fs.xpath('results/{}-{}.yaml'.format(
        base_name_out or fs.barename(script),
        get_content_hash(script)[::4]
    ))
    result, file = finder.dump_all_imports(script, result_file, sort=True)
    print(':v2t', 'dumped {} items. see result at "{}"'
          .format(len(result), file))


cli.add_cmd(check_on_lk_utils, 'check')
cli.add_cmd(make_tree)

if __name__ == '__main__':
    # pox -m sidework.tree_shaking -h
    # pox -m sidework.tree_shaking dump-all-imports
    #   sidework/tree_shaking/_test.py tree-shaking-test
    # pox -m sidework.tree_shaking check
    # pox -m sidework.tree_shaking dump-all-imports
    #   depsland/__main__.py depsland
    #       prepare: make sure `chore/site_packages` latest:
    #           pox sidework/merge_external_venv_to_local_pypi.py .
    #           pox build/init.py make-site-packages --remove-exists
    # pox -m sidework.tree_shaking make-tree <output_dir>
    cli.run()
