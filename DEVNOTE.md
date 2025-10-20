# Development Guide

## Init Project

1.  install dependencies

    ```sh
    cd <depsland>
    poetry env use <python_3.12>
    poetry install --no-root
    ```

2.  python standalone version

    download from python standalone releases: 
    https://github.com/indygreg/python-build-standalone/releases
    
    ps: help to get direct download link:

    ```sh
    poetry run python build/init.py help-me-choose-python
    ```

    **currently we use python 3.12.**

    more details see `python/README.zh.md`.

3.  self pypi folder

    if you have an old depsland project on another pc, you can copy its 
    `<depsland>/pypi` folder and overwrite here.

    otherwise create empty indexes by command:

    ```sh
    # init "pypi" folder
    poetry run python build/init.py init-pypi-blank pypi
    
    # build pypi index
    poetry run python build/init.py rebuild-pypi-index
    ```

3.  make site-packages folder

    ```sh
    # if poetry.lock is updated, run:
    poetry run python sidework/merge_external_venv_to_local_pypi.py .
    
    poetry run python build/init.py make-site-packages --remove-exists
    ```

5.  setup external project "python-tree-shaking"

    ```sh
    git clone <python_tree_shaking_project>
    cd python-tree-shaking
    poetry env use <python_3.12>
    poetry install --no-root
    
    cd <depsland_project>
    poetry run python -m lk_utils mklink <poetry_venv_site_packages> chore/venv
    poetry run python build/init.py make-minified-site-packages
    ```

## Misc

If you are using PyCharm, mark the following folders excluded in case indexing 
time too long:

- apps
- chore
- dist
- oss
- pypi
- python
- temp

## Run Depsland GUI

```sh
poetry run python -m depsland launch-gui
```

if app crashed on windows, should manually kill the process:

```sh
# find the process id
netstat -ano | find '2028'
# kill the process
taskkill /F /PID <pid>
```

## Serving Wiki

We use VitePress to build Wiki docs.

```shell
cd wiki
pnpm run docs:dev
# then visit http://localhost:5173
```

## Lock Requirements

first make sure poetry has synced `poetry.lock` file.

use script from https://github.com/likianta/poetry-extensions to lock 
requirements:

```sh
git clone <poetry_extensions_repo>
cd <poetry_extensions_repo>
# poetry install --no-root
poetry run python poxtry_extensions/poetry_export.py <depsland_project>
```

it generates/updates `<depsland_project>/requirements.lock` file, which is used 
for `build/init.py:download_requirements`.

## Build Depsland As Standalone Application

### Build An Offline Version

...

### Build An Internet Version

first create a config file at `tests/config/depsland.yaml`:

```yaml
oss:
    server: aliyun
    config:
        access_key: <your_access_key>
        secret_key: <your_secret_key>
        endpoint: oss-cn-shanghai.aliyuncs.com
        bucket: <your_bucket>
```

you need to purchase an aliyun oss service to fill the config.

then run the following command:

```nushell
# tell depsland to redirect config to custom path
$env.DEPSLAND_CONFIG_ROOT = 'tests/config'
poetry run python build/build.py full-build ailyun -p blank
```
