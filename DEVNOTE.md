# Devnote

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
