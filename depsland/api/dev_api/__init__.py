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
from .index import view_index
from .init import init
from .offline_build import main as build_offline
from .publish import main as publish
