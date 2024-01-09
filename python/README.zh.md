# 使用独立版 Python

## 下载

下载地址: https://github.com/indygreg/python-build-standalone/releases

如何选择我要的版本:

- macos (intel): `cpython-<version>-x86_64-apple-darwin-install_only.tar.gz`

    示例: "cpython-3.12.1+20240107-x86_64-apple-darwin-install_only.tar.gz"

- windows: `cpython-<version>-x86_64-pc-windows-msvc-shared-install_only.tar.gz`

    示例: "cpython-3.12.1+20240107-x86_64-pc-windows-msvc-shared-install_only.tar.gz"

    注意: 选择带有 "shared" 的文件, 不要 "static" 的. 因为后者无法安装 requests, numpy 等依赖了 dll 文件的第三方库.

你也可以使用 `build/self_build.py help-me-choose-pyversion` 来获取最新链接.

## 安装

> 以下示例基于 macos.

解压缩到本目录, 如下结构:

```
current_dir
|= bin
    |- python3.12
    |- pip
    |- ...
|= lib
    |= python3.12
        |= site-packages
            |= pip
            |= ...
    |= ...
|= share
|- README.md  # 这是本文档
```

## 安装 Depsland 所需的依赖

```sh
pox sidework/prepare_packages.py preindex requirements.lock
pox sidework/prepare_packages.py link-venv requirements.lock python/lib/python3.12/site-packages
```

此外, 还建议安装 wheel:

```sh
./python/bin/python3 -m pip install wheel --no-warn-script-location --disable-pip-version-check
```

### PySide6 Lite

> 注意: 目前仅支持 windows.

使用 qmlease 项目下的 `sidework/pyside_package_tailor` 生成一个 "pyside6_lite" (文件夹), 将它复制到 site-packages 下.

## 设置为本项目默认解释器 (可选)

以 pycharm 为例, 在 settings - project - project interpreter 中选择 `<depsland_proj>/python/bin/python3` 为解释器.
