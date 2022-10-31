
1. init manifest file

    ```sh
    py -m depsland init ./unittests/data/hello_world_demo_project/manifest.json -n "Hello World"
    ```

2. edit manifest file

    ```json
    {
        "appid": "hello_world",
        "name": "Hello World",
        "version": "0.1.0",
        "assets": {
            "src": "all"
        },
        "dependencies": {
            "lk-logger": ""
        }
    }
    ```

3. upload hello world project

    ```sh
    py -m depsland upload ./unittests/data/hello_world_demo_project/manifest.json
    ```
