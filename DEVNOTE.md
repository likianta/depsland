# Development Guide

## Init Project

1. poetry

    here are poetry commands alias for my personal use:

    ```yaml
    po: poetry
    por: poetry run
    pox: poetry run python
    ```

    ```sh
    # make venv
    po install --no-root
    ```

2. python standalone version

    download from python standalone releases: https://github.com/indygreg/python-build-standalone/releases

    currently we choose 3.12 version.

    more details to see `python/README.zh.md`.

3. a self pypi folder

    ```sh
    # download packages
    pox build/init.py download-requirements

    # build pypi index
    pox build/init.py self-build-pypi-index
    ```

3. make site-packages folder

    ```sh
    pox build/init.py make-site-packages
    ```

## Run Depsland GUI

```sh
pox -m depsland launch-gui
```

if app crashed on windows, should manually kill the process:

```sh
# find the process id
netstat -ano | find '2028'
# kill the process
taskkill /F /PID <pid>
```

## Lock Requirements

first make sure poetry has synced `poetry.lock` file.

use script from https://github.com/likianta/poetry-extensions to lock requirements:

```sh
git clone <poetry_extensions_repo>
cd <poetry_extensions_repo>
# po install --no-root
pox poxtry_extensions/poetry_export.py <depsland_project>
```

it generates/updates `<depsland_project>/requirements.lock` file, which is used for `build/init.py:download_requirements`.

## Build Depsland As Standalone Application

### Build An Offline Version

...

### Build An Intenet Version

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
pox build/build.py full-build ailyun
```
