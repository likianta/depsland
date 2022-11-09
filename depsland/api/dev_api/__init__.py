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
from .build import build
from .init import init
from .publish import main as publish
