
## Init

```sh
poetry run python -m depsland -h
poetry run python -m depsland init demo/hello-world

cd demo/hello-world
poetry install --no-root
```

## Build

1. bump version of `demo/hello-world/manifest.json : version`
2. set OSS access key and secret key in `config/depsland.yaml`
3. various of publish commands:

    ```sh
    # default
    poetry run python -m depsland publish demo/hello-world
    
    # or, fresh build (ignores history versions)
    poetry run python -m depsland publish demo/hello-world -f
   
    # or, upload dependencies to OSS
    poetry run python -m depsland publish demo/hello-world -d
    ```
