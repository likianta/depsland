# DEPSLAND_PROJECT

```
|= DEPSLAND_PROJECT
    |= depsland
    |= venv_home
    |= ...
```

# VENV_HOME

```
|= VENV_HOME (DEPSLAND_PROJECT/venv_home)
    |= python39
        |- python-3.9.5-embed-amd64.zip
        |= bin          : extracted from 'python-3.9.5-embed-amd64.zip'
            |- python.exe
            |- python39.dll
            |- python39.zip
            |- ...
        |= downloads    : the downloaded third library (.whl file)
            |- xxx.whl
            |- ...
        |= lib          : the third library (extracted from '../downlods/*.whl')
            |= xxx
            |= xxx-0.0.1.dist-info
            |= ...
        |= lib_extra
            |= lib_pip  : added follow the guide `setup-embed-python.md`
                |= pip
                |= pip-21.1.2.dist-info
                |= pkg_resources
                |= setuptools
                |= setuptools-57.0.0.dist-info
            |= lib_tk   : added follow the guide `setup-embed-python.md`
                |= tcl
                |= tkinter
                |- tcl86t.dll
                |- tk86t.dll
                |- _tkinter.pyd
        |= scripts      : added follow the guide `TODO`
            |- pip.exe
            |- ...
        |= venv
            |= hello_world_venv
                |- python.exe           : from `../../bin`
                |- python39.dll         : from `../../bin`
                |- python39.zip         : from `../../bin`
                |- ...                  : from `../../bin`
                |= lib
                    |= site-packages    : from `../../lib_extra/*` and 
                    |                   : `../../lib`
                        |= xxx
                        |= xxx-0.0.1.dist-info
                        |= ...
                |= scripts              : from `../../scripts`
                    |- pip.exe
                    |- ...
```
