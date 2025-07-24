Some dependencies for Depsland have a big size, they are heavy to compress and 
transfer, and python-tree-shaking can't shrink them well.

So we substitute them with custom packages, which are listed in this folder. 
The custom packages are disguised with the same name of them, but expose a few 
of "unused" interface objects.

The custom packages are used in:

- /build/build_tool/self_build.py
