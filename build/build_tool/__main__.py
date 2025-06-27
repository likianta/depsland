if __name__ == '__main__':
    __package__ = 'build_tool'
    
    from lk_utils.importer import load_package
    load_package('build/build_tool')

from argsense import cli

from .launcher_builder import add_icon_to_exe
from .launcher_builder import bat_2_exe as _b2e
from .minifier import minify_dependencies
from .self_build import build_dist
from .version_bump import bump_version

cli.add_cmd(bump_version)


@cli
def build_depsland_standalone(
    new_version: str = None,
    minify_deps: bool = False,
    **kwargs
) -> None:
    """
    params:
        new_version (-v):
        minify_deps (-m):
        **kwargs:
            oss_scheme (-o): aliyun | local
            pypi_scheme (-p): blank | full
    """
    new_version = bump_version(new_version)
    if minify_deps:
        minify_dependencies()
    build_dist(version=new_version, **kwargs)


cli.add_cmd(add_icon_to_exe, 'add-icon-to-exe')
cli.add_cmd(_b2e, 'bat-to-exe')


@cli
def rebuild_all_executebles(switches: str = '111111') -> None:
    iter_ = iter(switches)
    if next(iter_) == '1':
        _b2e('build/exe/depsland-cli.bat',
             show_console=True,
             uac_admin=False)
    if next(iter_) == '1':
        _b2e('build/exe/depsland-gui.bat',
             show_console=False,
             uac_admin=False)
    if next(iter_) == '1':
        _b2e('build/exe/depsland-gui-debug.bat',
             show_console=True,
             uac_admin=True)
    if next(iter_) == '1':
        _b2e('build/exe/depsland-runapp.bat',
             show_console=False,
             uac_admin=False,
             icon='build/icon/python.ico')
    if next(iter_) == '1':
        _b2e('build/exe/depsland-runapp-console.bat',
             show_console=True,
             uac_admin=False,
             icon='build/icon/python.ico')
    if next(iter_) == '1':
        _b2e('build/exe/depsland-runapp-debug.bat',
             show_console=True,
             uac_admin=True,
             icon='build/icon/python.ico')


if __name__ == '__main__':
    # pox build/build_tool/__main__.py -h
    
    # pox build/build_tool/__main__.py build-depsland-standalone -h
    # pox build/build_tool/__main__.py build-depsland-standalone -m
    #   --oss-scheme aliyun
    #       prerequisites:
    #           1. set environment variable:
    #               $env.DEPSLAND_CONFIG_ROOT = 'test/_config'
    #           2. make sure poetry.lock is latest.
    # pox build/build_tool/__main__.py build-depsland-standalone -M
    #   --oss-scheme aliyun --pypi-scheme full
    
    # pox build/build_tool/__main__.py bat-to-exe
    #   build/exe/depsland-cli.bat -c -U
    # pox build/build_tool/__main__.py bat-to-exe
    #   build/exe/depsland-gui.bat -C -U
    # pox build/build_tool/__main__.py bat-to-exe
    #   build/exe/depsland-gui-debug.bat -c -u
    # pox build/build_tool/__main__.py bat-to-exe
    #   build/exe/depsland-runapp.bat -C -U --icon build/icon/python.ico
    # pox build/build_tool/__main__.py bat-to-exe
    #   build/exe/depsland-runapp-console.bat -c -U --icon build/icon/python.ico
    # pox build/build_tool/__main__.py bat-to-exe
    #   build/exe/depsland-runapp-debug.bat -c -u --icon build/icon/python.ico
    cli.run()
