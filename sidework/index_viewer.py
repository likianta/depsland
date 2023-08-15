"""
usage:
    if you found the dependencies are not parsed correctly, you can:
        py sidework/index_viewer.py :false :false :true :false
"""
import os

from argsense import cli


@cli.cmd()
def main(
        show_name_2_versions=True,
        show_name_id_2_paths=True,
        show_dependencies=True,
        show_updates=True,
        pypi_root: str = None,
):
    """
    kwargs:
        show_name_2_versions (-s0):
        show_name_id_2_paths (-s1):
        show_dependencies (-s2):
        show_updates (-s3):
        pypi_root (-p):
    """
    if pypi_root:
        os.environ['DEPSLAND_PYPI_ROOT'] = pypi_root
    
    from depsland import pypi
    
    if show_name_2_versions:
        print(':l', pypi.name_2_versions)
    if show_name_id_2_paths:
        print(':l', pypi.name_id_2_paths)
    if show_dependencies:
        print(':l', pypi.dependencies)
    if show_updates:
        print(':l', pypi.updates)


if __name__ == '__main__':
    cli.run(main)
