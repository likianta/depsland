import re

from lk_utils import fs
from lk_utils import timestamp

import depsland


def bump_version(new_ver: str = None) -> str:
    old_ver = depsland.__version__
    if new_ver is None:
        new_ver = depsland.verspec.minorly_bump_version(old_ver)
    new_dps_ver = re.match(r'(.+)([ab]\d+)?$', new_ver).group(1)
    print('{} -> {}'.format(old_ver, new_ver), ':r2')
    
    _replace_version(
        'depsland/__init__.py',
        "__version__ = '{}'\n__date__ = '{}'"
        .format(old_ver, depsland.__date__),
        "__version__ = '{}'\n__date__ = '{}'"
        .format(new_ver, timestamp('y-m-d')),
    )
    
    # -- A
    # _replace_version(
    #     'manifest.json',
    #     '"version": "{}"'.format(old_ver),
    #     '"version": "{}"'.format(new_ver),
    # )
    # -- B
    content: str = fs.load('manifest.json', 'plain')
    content = content.replace(
        '"version": "{}"'.format(old_ver),
        '"version": "{}"'.format(new_ver),
        1
    )
    content = re.sub(
        r'"depsland_version": ".+"',
        '"depsland_version": "{}"'.format(new_dps_ver),
        content
    )
    fs.dump(content, 'manifest.json', 'plain')
    
    # -- A
    _replace_version(
        'pyproject.toml',
        'version = "{}"'.format(old_ver),
        'version = "{}"'.format(new_ver),
    )
    # -- B
    # content: str = fs.load('pyproject.toml', 'plain')
    # content = re.sub(
    #     r'\nversion = "{}"'.format(old_ver),
    #     '\nversion = "{}"'.format(new_ver),
    #     content
    # )
    # content = re.sub(
    #     r'\ndepsland_version = ".+"',
    #     '\ndepsland_version = "{}"'.format(new_dps_ver),
    #     content
    # )
    # fs.dump(content, 'pyproject.toml', 'plain')
    
    return new_ver


def _replace_version(file: str, old_text: str, new_text: str) -> None:
    content = fs.load(file, 'plain')
    content = content.replace(old_text, new_text, 1)
    fs.dump(content, file, 'plain')
