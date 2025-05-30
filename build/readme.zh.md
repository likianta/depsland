# 构建说明

## 准备工作

### 生成 exe 文件

在 `./exe` 目录下, 每个 bat 文件, 都必须有一个同名的 exe 文件. 如下:

```
depsland
|- build
    |- exe
        |- depsland-cli.bat
        |- depsland-cli.exe
        |- depsland-gui.bat
        |- depsland-gui.exe
        |- depsland-gui-debug.bat
        |- depsland-gui-debug.exe
        |- depsland-runapp.bat
        |- depsland-runapp.exe
        |- depsland-runapp-console.bat
        |- depsland-runapp-console.exe
        |- depsland-runapp-debug.bat
        |- depsland-runapp-debug.exe
```

如果发现有缺少 exe 文件的情况, 或者 bat 的内容发生了改变, 则需要使用 bat-2-exe 工具生成新的 exe.

你需要一台 windows 电脑, 在命令行完成. 所有命令见 `build/build_tool/__main__.py : if __name__ == '__main__' : comment`.

## 打包

### 生成独立的应用

1. 检查版本号

    1. `depsland/__init__.py` 的版本号 (`__version__`) 要求:
        
        1. 可以是正式版或预览版
        2. 该版本号不存在于 `dist` 目录. 例如, 如果版本号是 '0.5.3b7', 则 `dist` 目录下不能有 "depsland-setup-0.5.3b7" 文件夹
        
            如果 dist 下的文件夹已存在, 则应该提升版本号. 例如 '0.5.3b7' 提升为 '0.5.3b8'.
            
    2. `depsland/__init__.py` 的日期 (`__date__`) 应更新为当前日期

2. (可选) 更新 `manifest.json`

3. 生成应用

    windows terminal (powershell):

    ```sh
    $env:DEPSLAND_CONFIG_ROOT="tests/config"
    py build/build.py full-build aliyun
    ```

### 生成精简版的独立应用

精简版的应用是在独立版应用的基础上, 利用 "树摇" 技术对依赖包的体积进行大幅裁剪. 关于 "树摇" 的技术说明, 请参考 https://github.com/likianta/python-tree-shaking .

1. 同步版本号

### 生成 whl 文件

1. 检查版本号是否为最新

    1. `depsland/__init__.py` 的版本号 (`__version__`) 应更新为正式版本
    
        正例:
            
        - `__version__ = '0.5.0'`
        - `__version__ = '0.5.1'`
        - `__version__ = '0.5.2'`
        - `__version__ = '0.6.0'`
        - ...
        
        反例:
            
        - `__version__ = '0.5.0a0'`
        - `__version__ = '0.5.1b2'`
        - ...
    
    2. `depsland/__init__.py` 的日期 (`__date__`) 应更新为当前日期
    
        示例:
        
        - `__date__ = '2023-02-21'`
    
    3. `pyproject.toml` 的版本号更新
    
        如果发布的是预览版, 则使用 alpha/beta 版号.
        
        如果发布的是正式版 (要上传到 pypi), 则去掉 alpha/beta 版号.

2. 检查 `depsland/chore/*`

    如果自上次发布以来, 你的 build, config, sidework 等目录有文件更新, 则需要重新生成 `depsland/chore`.
    
    命令:
        
    ```sh
    py build/backup_project_resources.py
    ```

2. 生成 whl 文件

    ```sh
    poetry build -f wheel
    ```
    
3. 如果是预览版, 则 pip 安装并测试; 如果是正式版, 则上传到 pypi:

    ```sh
    poetry publish
    ```

## 用户安装

1. 首先打包为独立应用, 制作成压缩文件
1. 分享该文件给用户 (体积约 120mb)
2. 用户收到后, 解压到任意目录 (推荐英文路径)
3. 运行 setup.exe

    截图:

    ![](.assets/readme.zh/image-20221031233240689.png "初次安装")
    
    ![](.assets/readme.zh/image-20221101003716782.png "升级")

4. 测试是否安装成功:

    1. 确认桌面上出现了 "Depsland.lnk" 的启动器
    2. 双击该启动器, 会看到如下界面:
    
        ...

## 常用命令备忘

self_build.py

```sh
py build/self_build.py -h

py build/self_build.py init pypi
py build/self_build.py init pypi_self

py build/self_build.py build
py build/self_build.py build -sd
py build/self_build.py build -sd -si

py build/self_build.py link
```

build.py

```sh
python/python.exe -m pip install -r requirements.lock --no-deps --no-warn-script-location --disable-pip-version-check

py build/build.py -h
py build/build.py full-build -h

py build/build.py full-build aliyun
py build/build.py full-build aliyun -p full
py build/build.py full-build aliyun -p least

py build/build.py bat-2-exe build/exe/depsland.bat
py build/build.py bat-2-exe build/exe/depsland-sui.bat -u
py build/build.py bat-2-exe build/exe/depsland-suw.bat -C -u
py build/build.py bat-2-exe build/exe/desktop.bat -u
py build/build.py bat-2-exe build/exe/setup.bat -C -u
```

unittests

```sh
py -m depsland publish unittests/demo_apps/hello-world/manifest.json
py -m depsland publish unittests/demo_apps/hello-world-gui/manifest.json
```
