"""
1. build

    1. bump depsland version (`depsland/__init__.py`)
    2. run command:
    
        ```sh
        py build/build.py full-build :false
        py -m lk_utils mklink python dist/depsland-<version>
        ```
    
2. setup
    
    1. double click `dist/depsland-<version>/setup.exe`
    2. choose the default install location
    
3. upload

    1. bump manifest version (`manifest.json`)
    2. run command:
    
        ```sh
        py -m depsland upload
        ```
    
4. test `self-upgrade`

    1. open a new terminal
    2. run command:
    
        ```sh
        # depsland self-upgrade -h
        depsland self-upgrade
        ```
    
    ... fix anything crashed, til it passed through.
"""
