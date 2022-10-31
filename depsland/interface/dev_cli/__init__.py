"""
command list:
    depsland --version
    depsland --help

    depsland init

    depsland add <package>
    depsland remove <package>
    depsland update [package]

    depsland list
    depsland show <package>
"""
from .init import init
from .upload import main as upload
