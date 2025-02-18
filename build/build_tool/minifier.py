from lk_utils import fs
from lk_utils import run_cmd_args

from depsland.utils import make_temp_dir
from .poetry import poetry

abspath = lambda x: fs.xpath(x)  # noqa


def minify_dependencies() -> None:
    if not fs.exists('chore/venv'):
        raise Exception(
            'please link original venv path to "chore/venv" to continue. the '
            'command is: `python -m lk_utils mklink {}/Lib/site-packages '
            'chore/venv`'.format(
                fs.normpath(run_cmd_args(
                    'poetry', 'env', 'info', '--path', '--no-ansi',
                    cwd=abspath('../../')
                ))
            )
        )
    
    print('build module graphs')
    poetry.run(
        'python', '-m', 'tree_shaking', 'build-module-graphs',
        abspath('_tree_shaking_model.yaml'),
        cwd=abspath('../../../python-tree-shaking'),
    )
    
    print('build tree')
    poetry.run(
        'python', '-m', 'tree_shaking', 'dump-tree',
        abspath('_tree_shaking_model.yaml'),
        # x := abspath('../../temp/{}'.format(timestamp('ymd-hns'))),
        x := make_temp_dir(),
        cwd=abspath('../../../python-tree-shaking'),
    )
    print(x, ':v')
    
    # postfix
    # related: [./_tree_shaking_modules.yaml : ignores]
    fs.remove(f'{x}/venv/numpy.libs')
    _make_empty_package(f'{x}/venv/matplotlib')
    _make_empty_package(f'{x}/venv/numpy')
    _make_empty_package(f'{x}/venv/pandas')
    
    fs.move(f'{x}/venv', 'chore/minified_site_packages', True)


def _make_empty_package(path) -> None:
    if fs.exists(path):
        fs.remove(path)
    fs.make_dir(path)
    fs.dump('', f'{path}/__init__.py')
