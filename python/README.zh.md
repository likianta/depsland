# 使用独立版 Python

> 注: 以下命令行示例中, 使用 `pox` 表示 `poetry run python`. 请参考 `DEVNOTE.md` 了解在此文之前应做的事情.

## 下载

下载地址: https://github.com/indygreg/python-build-standalone/releases

如何选择我要的版本:

使用 `build/init.py : help_me_choose_python` 来获取合适的版本的下载链接.

## 安装

> 以下示例基于 macos.

解压缩到本项目根目录下, 如下结构:

```
<depsland_project>
|= python
    |= bin
        |- python3.12
        |- pip
        |- ...
    |= lib
        |= python3.12
            |= site-packages
                |= pip
                |- ...
        |- ...
    |- ...
    |- README.zh.md  # 这是本文档
```

## 安装 Depsland 所需的依赖

```sh
pox build/init.py download-requirements
pox build/init.py make-site-packages
```

---

## PySide6 Lite

> 注意: 目前仅支持 windows.

使用 qmlease 项目下的 `sidework/pyside_package_tailor` 生成一个 "pyside6_lite" (文件夹), 将它复制到 site-packages 下.
