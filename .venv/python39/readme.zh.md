# depsland venv 虚拟环境目录创建流程

1. 从 python 官网下载嵌入式版本的 python: 'python-3.9.7-embed-amd64.zip'

2. 解压到 'embed_venv'

   ```
   my_downloads
   |- python-3.9.7-embed-amd64.zip ---+
   |                                  |  # 1. 下载到本地后, 解压缩
   |= python-3.9.7-embed-amd64 <------+
      |- python.exe         |
      |- ...                |
                            |
   depsland_project         |
   |= .venv                 |
      |= python39           |
         |= embed_venv <----+  # 2. 文件夹重命名并放在这个位置
            |- python.exe
            |- ...
   ```

3. 将 `~/embed_venv/python39._pth` 重命名为 `~/embed_venv/python39._pth.bak`

   ```
   depsland_project
   |= .venv
      |= python39
         |= embed_venv
            |- python39._pth -> python39._pth.bak
   ```

4. 创建空文件夹

   ```
   depsland_project
   |= .venv
      |= python39
         |= embed_venv
            |= dlls     # 1. 创建空文件夹
            |= scripts  # 2.
            |= lib      # 3.
               |= site-packages  # 4.
   ```

5. 依次从 pypi 上下载 'pip-21.2.4-py3-none-any.whl', 'setuptools-58.0.4-py3-none-any.whl', '
   urllib3-1.25.11-py2.py3-none-any.whl' (注意使用特定的版本号, 不是越新越好.)

6. 按照下面的流程图放置:

   ```
   my_downloads
   |- pip-21.2.4-py3-none-any.whl ------------+  # 1. 解压到文件夹
   |- setuptools-58.0.4-py3-none-any.whl -----|---+  # 2. 解压到文件夹
   |- urllib3-1.25.11-py2.py3-none-any.whl ---|---|---+  # 3. 解压到文件夹
   |                                          |   |   |
   |= pip-21.2.4-py3-none-any <---------------+   |   |
      |= pip                                      |   |
      |= pip-21.2.4.dist-info                     |   |
   |= setuptools-58.0.4-py3-none-any <------------+   |
      |= _distutils_hack                              |
      |= pkg_resources                                |
      |= setuptools                                   |
      |= setuptools-58.0.4.dist-info                  |
      |- distutils-precedence.pth                     |
   |= urllib3-1.25.11-py2.py3-none-any <--------------+
      |= urllib3
      |= urllib3-1.25.11.dist-info
   ```

   ```
   my_downloads
   |= pip-21.2.4-py3-none-any
      |= pip --------------------------+  # 移动文件夹...
      |= pip-21.2.4.dist-info ---------|------+
   |= setuptools-58.0.4-py3-none-any   |      |
      |= _distutils_hack --------------|------|---+
      |= pkg_resources ----------------|------|---|---+
      |= setuptools -------------------|------|---|---|---+
      |= setuptools-58.0.4.dist-info --|------|---|---|---|---+
      |- distutils-precedence.pth -----|------|---|---|---|---|---+
   |= urllib3-1.25.11-py2.py3-none-any |      |   |   |   |   |   |
      |= urllib3 ----------------------|------|---|---|---|---|---|---+
      |= urllib3-1.25.11.dist-info     |      |   |   |   |   |   |   |
                                       |      |   |   |   |   |   |   |
   depsland_project                    |      |   |   |   |   |   |   |
   |= .venv                            |      |   |   |   |   |   |   |
      |= python39                      |      |   |   |   |   |   |   |
         |= embed_venv                 |      |   |   |   |   |   |   |
            |= lib                     |      |   |   |   |   |   |   |
               |= site-packages        |      |   |   |   |   |   |   |
                  |= _distutils_hack <-|------|---+   |   |   |   |   |
                  |= pkg_resources <---|------|-------+   |   |   |   |
                  |= pip <-------------+      |           |   |   |   |
                  |= pip-21.2.4.dist-info <---+           |   |   |   |
                  |= setuptools <-------------------------+   |   |   |
                  |= setuptools-58.0.4.dist-info <------------+   |   |
                  |= urllib3 <------------------------------------|---+
                  |- distutils-precedence.pth <-------------------+
   ```
   
   ```
   depsland_project
   |= .venv
      |= python39
         |= embed_venv
            |= lib
            |= site-packages
               |= pip
                  |= _vendor
                     |  # 1. 该目录下原有一个 'urllib3' 文件夹, 将它重命名 (或者
                     |  #    删掉)
                     |= urllib3 -> urllib3.bak
                     |= urllib3 <---+
               |                    |  # 2. 然后将 site-packages 下的 'urllib3'
               |= urllib3 ----------+  #    移放到此处
   ```

7. 测试: 打开 CMD, 输入下面的指令 (将指令中的花括号替换为您的真实路径)

   ```
   {depsland_project}/.venv/python39/embed_venv/python.exe -m pip --version
   ```

   ```
   {depsland_project}/.venv/python39/embed_venv/python.exe -m pip install lk-logger
   ```
