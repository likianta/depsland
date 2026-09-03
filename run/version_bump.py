"""
This script is going to replace `build/build_standalone/standalone.py
:bump_version`.
"""

from argsense import cli
from depsland import __version__ as current_depsland_version
from depsland.api.dev_api.build_project import bump_version_inplaces
from depsland.utils import bump_version as bump_least_version
from neoprint import print


@cli
def bump_version(new_ver: str = '') -> None:
    if not new_ver:
        new_ver = bump_least_version(current_depsland_version)
    print(
        ':r2',
        'bump version: {} -> {}'.format(current_depsland_version, new_ver),
    )
    bump_version_inplaces(
        'pyproject.toml',
        'depsland/__init__.py',
        'sidework/depsland_updater/pyproject.toml',
        new_version=new_ver,
    )


if __name__ == '__main__':
    # python run/version_bump.py
    # python run/version_bump.py <new_version>
    cli.run(bump_version)
