"""
1. prepare a test project -- 'hello world'

    location: `unittests/demo_project/hello_world`

2. init

    ```sh
    cd unittests/demo_project/hello_world
    py -m depsland init
    ```

3. update manifest file (or just bump its version for next build).

4. build

    ```sh
    py -m depsland build
    ```
    
    it will generates:
    
    `unittests/demo_project/hello_world/dist/hello_world-<version>` (dir)

5. publish

    make sure we've configured the oss server as 'local'.

    run command:
    
    ```sh
    py -m depsland publish
    ```
    
    it will generates:
    
    `unittests/demo_project/hello_world/dist/hello_world-<version>/.oss` (dir)

"""
