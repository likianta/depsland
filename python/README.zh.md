# 下载便携版 Python

下载地址: https://github.com/indygreg/python-build-standalone/releases/tag/20221002

如何选择我要的版本:

- macos (intel): `cpython-<version>-x86_64-apple-darwin-install_only.tar.gz`

    示例: "cpython-3.10.7+20221002-x86_64-apple-darwin-install_only.tar.gz"

- windows: `cpython-<version>-x86_64-pc-windows-msvc-shared-install_only.tar.gz`

    示例: "cpython-3.10.7+20221002-x86_64-pc-windows-msvc-shared-install_only.tar.gz"

# 安装 python

> 以下示例基于 macos.

解压缩到本目录, 如下结构:

```
current_dir
|= bin
    |- python3.10
    |- pip
    |- ...
|= include
    |= python3.10
        |= site-packages
            |= pip
            |= ...
    |= ...
|= lib
|= share
|- README.md  # 这是本文档
```

# 设置为本项目默认解释器

以 pycharm 为例, 在 settings - project - project interpreter 中选择 `<depsland_proj>/python/bin/python3.10` 为解释器.

# 安装依赖

```sh
python/bin/python3.10 -m pip install --no-warn-script-location --disable-pip-version-check -r requirements.txt
```
