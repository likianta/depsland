import typing as tp

import tree_shaking
from lk_utils import fs

from ..utils import hash_content
from ..utils import hash_file_content
from ..venv import get_venv_root


def get_cache_file(
    project_directory,
    base_locked: tp.Literal['poetry.lock', 'uv.lock'] = 'uv.lock',
) -> str:
    # caution: the file may not exist, you should check it before using it.
    return '{}/.depsland/{}.pkl'.format(
        project_directory,
        hash_content(
            # this means: if any one of (uv.lock / poetry.lock / tree-shaking
            # implicit hooks file) changed, rebuild the mini_deps cache.
            '{}:{}'.format(
                hash_file_content(
                    '{}/{}'.format(project_directory, base_locked)
                ),
                hash_file_content(tree_shaking.implicit_hooks_file),
            )
        ),
    )


def minify_dependencies(
    project_directory: str,
    entries: tp.Sequence[str],
    search_paths: tp.Sequence[str] = ('.depsland/orig_deps', '.'),
    base_locked: tp.Literal['poetry.lock', 'uv.lock'] = 'uv.lock',
) -> None:
    """
    folder structure:
        <target_project>
        |= .depsland
            |= orig_deps
            |= mini_deps
            |- tree_shaking_model.json
    the `<target_project>/.depsland/mini_deps` path will be added to
    `sys.path` in the runtime, see also `python/sitecustomize.py` for
    details.
    """
    dot_dps_dir = '{}/.depsland'.format(project_directory)
    print(dot_dps_dir, ':vn')

    orig_deps_dir = '{}/orig_deps'.format(dot_dps_dir)
    mini_deps_dir = '{}/mini_deps'.format(dot_dps_dir)
    mini_deps_cache_file = get_cache_file(project_directory, base_locked)

    if fs.exist(mini_deps_cache_file):
        assert not fs.empty(mini_deps_dir)
        return

    if fs.exist(mini_deps_dir):
        print('incrementally minify dependencies', ':p')
    else:
        print('first time minify dependencies', ':p')

    fs.make_dir(dot_dps_dir)
    fs.make_link(
        get_venv_root(project_directory, base_locked.removesuffix('.lock')),
        orig_deps_dir,
    )

    fs.dump(
        {
            'root': '..',
            'entries': entries,
            'search_paths': list(search_paths),
            'export': {
                'source': '.depsland/orig_deps',
                'target': '.depsland/mini_deps',
            },
        },
        model_file := '{}/tree_shaking_model.json'.format(dot_dps_dir),
    )

    tree_shaking.build_module_graphs(model_file)
    tree_shaking.dump_tree(model_file)

    from ..manifest.assets import index_assets

    mini_deps_assets_info = index_assets(
        assets0=['.depsland/mini_deps/*'], start_directory=project_directory
    )
    fs.dump(mini_deps_assets_info, mini_deps_cache_file)
