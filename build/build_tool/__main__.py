if __name__ == '__main__':
    __package__ = 'build_tool'
    from lk_utils.importer import load_package
    load_package('build/build_tool')

from argsense import cli

from .launcher_builder import bat_2_exe
from .minifier import minify_dependencies
from .self_build import build_dist
from .version_bump import bump_version


@cli.cmd()
def build_depsland_standalone(
    new_version: str = None,
    minify_deps: bool = False,
    **kwargs
) -> None:
    """
    kwargs:
        new_version (-v):
        minify_deps (-m):
    """
    new_version = bump_version(new_version)
    if minify_deps:
        minify_dependencies()
    build_dist(version=new_version, **kwargs)


cli.add_cmd(bat_2_exe)


if __name__ == '__main__':
    # pox build/build_tool/__main__.py -h
    
    # pox build/build_tool/__main__.py build-depsland-standalone -h
    # pox build/build_tool/__main__.py build-depsland-standalone -m
    #   --oss-scheme aliyun
    #       prerequisites:
    #           1. set environment variable:
    #               $env.DEPSLAND_CONFIG_ROOT = 'tests/config'
    #           2. make sure poetry.lock is latest.
    # pox build/build_tool/__main__.py build-depsland-standalone -M
    #   --oss-scheme aliyun --pypi-scheme full
    
    # pox build/build_tool/__main__.py bat-2-exe
    #   build/exe/depsland-runapp-console.bat --icon build/icon/python.ico
    cli.run()
