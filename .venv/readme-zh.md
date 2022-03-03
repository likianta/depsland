# depsland venv 虚拟环境目录创建流程

> 注: 下面以 python 3.8 为例创建.

1. 从 python 官网下载嵌入式版本的 python: [python-3.8.10-embed-amd64.zip][1]

2. 假设下载到: 'downloads/python-3.8.10-embed-amd64.zip'

3. 将它在同目录下解压: 'downloads/python-3.8.10-embed-amd64/'

4. 然后移动到: 'depsland/.venv/python38/'

5. 在 'depsland/.venv/python38/' 目录下...
    1. 将 'python38._pth' 重命名为 'python38._pth.bak'
    2. 创建空文件夹
        1. dlls
        2. scripts
        3. lib
        4. lib/site-packages

6. 依次从 pypi 上下载:
    1. pip-21.2.4-py3-none-any.whl
    2. setuptools-58.0.4-py3-none-any.whl
    3. urllib3-1.25.11-py2.py3-none-any.whl

    (注意使用特定的版本号, 不是越新越好.)

7. 假设下载到:
    1. 'downloads/pip-21.2.4-py3-none-any.whl'
    2. 'downloads/setuptools-58.0.4-py3-none-any.whl'
    3. 'downloads/urllib3-1.25.11-py2.py3-none-any.whl'

8. 将它们在同目录下解压:
    1. 'downloads/pip-21.2.4-py3-none-any'
    2. 'downloads/setuptools-58.0.4-py3-none-any'
    3. 'downloads/urllib3-1.25.11-py2.py3-none-any'

9. 然后将里面的文件 (夹) 移动到:

    ```
    depsland
    |= .venv
       |= python38
          |= lib
             |= site-packages

                # 来自 pip-21.2.4-py3-none-any
                |= pip
                |= pip-21.2.4.dist-info

                # 来自 setuptools-58.0.4-py3-none-any
                |= _distutils_hack
                |= pkg_resources
                |= setuptools
                |= setuptools-58.0.4.dist-info
                |- distutils-precedence.pth

                # 来自 urllib3-1.25.11-py2.py3-none-any
                |= urllib3
                |= urllib3-1.25.11.dist-info
    ```

10. 此外, 在 depsland/.venv/python38/lib/site-packages 目录下...
    1. 将 pip/_vendor/urllib3 删除
    2. 复制 urllib3 文件夹, 粘贴到 pip/_vendor/urllib3

11. 测试: 打开 CMD, 输入下面的指令 (将指令中尖括号中的内容替换为您的真实路径)

    ```
    <depsland>/.venv/python38/python.exe -m pip --version
    ```

    ```
    <depsland>/.venv/python38/python.exe -m pip install lk-logger
    ```

[1]: https://www.python.org/ftp/python/3.8.10/python-3.8.10-embed-amd64.zip
