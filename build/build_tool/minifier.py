import tree_shaking
from lk_utils import fs
from lk_utils import run_cmd_args


def minify_dependencies() -> None:
    if not fs.exists('chore/venv'):
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
    
    root = 'chore/_temp_minified_site_packages'
    tree_shaking.build_module_graphs(fs.xpath('_tree_shaking_model.yaml'))
    tree_shaking.dump_tree(fs.xpath('_tree_shaking_model.yaml'), root)
    
    # postfix
    # related: "./_tree_shaking_modules.yaml : ignores"
    fs.remove(f'{root}/venv/numpy.libs')
    _make_empty_package(f'{root}/venv/matplotlib')
    _make_empty_package(f'{root}/venv/numpy')
    _make_empty_package(f'{root}/venv/pandas')
    fs.make_link(f'{root}/venv', 'chore/site_packages')


def _make_empty_package(path: str) -> None:
    if fs.exist(path):
        fs.remove_tree(path)
    fs.make_dir(path)
    fs.dump('', f'{path}/__init__.py')
