# 如何下载嵌入式版本的 Python

Windows 从该网址下载: https://www.python.org/downloads/windows/

(TODO: 其他系统待补充)

建议选择较新的版本, 并选择带有 "embeddable" 字样的文件.

# 示例详解

> 以 Windows 系统 Python 3.9 为例, 请确保您的电脑已安装完整版的 Python 3.9 (假设位于 'C:/Program Files/Python39').

1. **下载**

    从 [官网](https://www.python.org/downloads/windows/) 下载 "Windows embeddable package (64-bit)" 到本地: `{depsland}/depsland_venv/python39/python-3.9.5-embed-amd64.zip`

    ![](.assets/20210620_105251.png)

2. **解压到 `{depsland}/depsland_venv/python39/bin`**

3. **删除 ._pth 文件**

    删除 `{depsland}/depsland_venv/python39/bin/python39._pth` 文件, 或者重命名为 "python39._pth.bak".

    ([参考链接][1])

4. **复制 tkinter 套件**

    首先, 在 `{depsland}/depsland_venv/python39/lib_extra` 目录下新建 'lib_tk' 文件夹.

    然后, 将本机安装的 Python 3.9 目录 (`C:/Program Files/Python39`) 中的以下文件 (夹) 复制过去:

    ```
    System Python 3.9                   Embed Python 3.9 
    (C:/Program Files/Python39)         ({depsland}/depsland_venv/python39/
    |                                    lib_extra/lib_tk)
    |= tcl ---------------------------> |= tcl
    |= Lib                              |
        |= tkinter -------------------> |= tkinter
    |= DLLs                             | 
        |- _tkinter.pyd --------------> |- _tkinter.pyd
        |- tcl86t.dll ----------------> |- tcl86t.dll
        |- tk86t.dll -----------------> |- tk86t.dll
    ```

    ([参考链接][2])

5. **复制 pip 文件**

    ```
    System Python 3.9                   Embed Python 3.9 
    (C:/Program Files/Python39/         ({depsland}/depsland_venv/python39/
     Lib/site-packages)                  lib_extra/lib_pip)
    |= pip ---------------------------> |= pip
    |= pip-21.1.2.dist-info ----------> |= pip-21.1.2.dist-info
    |= pkg_resources -----------------> |= pkg_resources
    |= setuptools --------------------> |= setuptools
    |= setuptools-57.0.0.dist-info ---> |= setuptools-57.0.0.dist-info
    ```

    ```
    System Python 3.9                   Embed Python 3.9 
    (C:/Program Files/Python39/         ({depsland}/depsland_venv/python39/
     Scripts)                            scripts)
    |- pip.exe -----------------------> |- pip.exe
    |- pip3.exe ----------------------> |- pip3.exe
    |- pip3.9.exe --------------------> |- pip.3.9exe
    ```

[1]: https://stackoverflow.com/questions/44443254/python-embeddable-zip-file-doesnt-include-lib-site-packages-in-sys-path

[2]: https://github.com/Likianta/pyportable-installer/blob/master/docs/add-tkinter-to-embed-python.md

[3]: :https://pip.pypa.io/en/stable/installing
