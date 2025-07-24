import tree_shaking
from lk_utils import fs
from lk_utils import run_cmd_args


def minify_dependencies() -> None:
    if not fs.exist('chore/venv'):
        raise Exception(
            'please link original venv path to "chore/venv" to continue. the '
            'command is: `python -m lk_utils mklink {}/Lib/site-packages '
            'chore/venv`'.format(
                fs.normpath(run_cmd_args(
                    'poetry', 'env', 'info', '--path', '--no-ansi',
                    cwd=fs.xpath('../../')
                ))
            )
        )
    
    temp_root = 'chore/_temp_minified_site_packages'
    tree_shaking.build_module_graphs(fs.xpath('_tree_shaking_model.yaml'))
    tree_shaking.dump_tree(fs.xpath('_tree_shaking_model.yaml'), temp_root)
    
    # postfix
    # related: "./_tree_shaking_modules.yaml : ignores"
    # fs.remove(f'{temp_root}/venv/numpy.libs')
    _make_disguised_packages(f'{temp_root}/venv')
    
    if not fs.exist('chore/site_packages'):
        fs.make_link(f'{temp_root}/venv', 'chore/site_packages')


def _make_disguised_packages(root_o: str) -> None:
    """
    doc: /chore/disguised_packages/readme.md
    """
    for pkg_name in ('matplotlib', 'numpy', 'pandas'):
        dir_o = f'{root_o}/{pkg_name}'
        if fs.exist(dir_o):
            if fs.islink(dir_o):
                continue
            else:
                raise Exception(dir_o)
        else:
            dir_i = f'chore/disguised_packages/{pkg_name}'
            fs.make_link(dir_i, dir_o)
