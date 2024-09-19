from lk_utils import fs
from lk_utils import timestamp

import depsland


def bump_version(new_ver: str = None) -> str:
    old_ver = depsland.__version__
    if new_ver is None:
        new_ver = depsland.verspec.minorly_bump_version(old_ver)
    print('{} -> {}'.format(old_ver, new_ver), ':r2')
    
    _replace_version(
        'depsland/__init__.py',
        "__version__ = '{}'\n__date__ = '{}'"
        .format(old_ver, depsland.__date__),
        "__version__ = '{}'\n__date__ = '{}'"
        .format(new_ver, timestamp('y-m-d')),
    )
    _replace_version(
        'manifest.json',
        '"version": "{}"'.format(old_ver),
        '"version": "{}"'.format(new_ver),
    )
    _replace_version(
        'pyproject.toml',
        'version = "{}"'.format(old_ver),
        'version = "{}"'.format(new_ver),
    )
    
    return new_ver


def _replace_version(file: str, old_text: str, new_text: str) -> None:
    content = fs.load(file, 'plain')
    content = content.replace(old_text, new_text, 1)
    fs.dump(content, file, 'plain')
