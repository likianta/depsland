# Structure

```
depsland
|= venv_home
    |= inventory
        |= {platform}
            |= {pyversion}
                |= bin
                |= cache
                |= downloads
                |= lib
                |= lib_extra
                    |= lib_pip
                    |= lib_tk
                |= scripts
                |- {embed_python_zip_file}
    |= venv_links
        |= {project_venv}
            |= dlls
            |= lib
                |= site-packages
            |= scripts
            |- {file_links_from_inventory_bin_dir}
```

# Example

```
depsland
|= venv_home
    |= inventory
        |= windows
            |= python39
                |= bin
                    |- python.exe
                    |- python3.dll
                    |- python39.dll
                    |- python39.zip
                    |- ...
                |= cache
                |= downloads
                    |- requests-2.26.0-py2.py3-none-any.whl
                    |- ...
                |= site-packages
                    |= requests
                    |= requests-2.26.0.dist-info
                    |= ...
                |= extra
                    |= pip_suits
                    |= tk_suits
                |= scripts
                    |- pip.exe
                    |- pip3.9.exe
                    |- wheel.exe
                    |- ...
                |- python-3.9.5-embed-amd64.zip
    |= venv_links
        |= hello_world_venv
            |= dlls
            |= lib
                |= site-packages
                    |~ pip
                    |~ pip-21.2.4.dist-info
                    |~ requests
                    |~ requests-2.26.0.dist-info
                    |~ setuptools
                    |~ setuptools-56.0.0.dist-info
                    |~ ...
            |= scripts
                |~ pip.exe
                |~ pip3.9.exe
                |~ wheel.exe
                |~ ...
            |~ python.exe
            |~ python3.dll
            |~ python39.dll
            |~ python39.zip
            |~ ...
```
