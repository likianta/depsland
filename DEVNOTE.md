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

    see `python/README.zh.md`.

3. a self pypi folder

    ```sh
    # download packages
    pox build/init.py download-requirements

    # build pypi index
    pox build/init.py self-build-pypi-index
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
