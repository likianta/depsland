
## 准备文件

1. 生成 exe 文件

    如果本目录下缺少以下文件:

    - depsland_setup.exe
    - depsland_desktop.exe

    则需要通过同名的 bat 文件来生成:

    1. 找一个 windows 系统的电脑
    2. 终端命令:

        ```sh
        py build/bat_2_exe.py build/depsland_setup.bat
        #   生成 depsland_setup.exe
        py build/bat_2_exe.py build/depsland_desktop.bat
        #   生成 depsland_desktop.exe
        ```

## 生成 depsland 安装包

1. 检查 `depslan/__init__.py` 的版本号 (`__version__`) 是否需要更新

    请注意, 该版本号必须不存在于 dist 目录下 (例如, 如果当前是 0.1.0 版本, 在 dist 目录下不可以有 "depsland-0.1.0" 目录).

    如果有的话, 要么手动删除该目录, 要么更新一下版本号.

2. 终端命令:

    ```sh
    # 整个过程很快, 在 1s 左右完成.
    py build/build.py build
    ```

3. 生成结果: `dist/depsland-<version>` (文件夹)

    该文件夹的体积在 140mb 左右 (压缩后约 55mb). 各部分占比如下:

    - depsland 源代码: 190kb (0.13%)
    - python 解释器: 90mb (64.29%)
    - depsland 依赖库: 50mb (35.71%)
    - 其他文件: 120kb (0.08%)

## 用户安装

1. 用户收到该安装包 (体积约 55mb)
2. 解压到任意目录 (推荐英文路径)
3. 运行 setup.exe

    截图:

    ![image-20221031233240689](.assets/readme.zh/image-20221031233240689.png "初次安装")
    
    ![image-20221101003716782](.assets/readme.zh/image-20221101003716782.png "升级")

4.   测试是否安装成功:

     1.   确认桌面上出现了 "Depsland.exe" 的启动器

     2.   双击该启动器, 看是否会出现欢迎界面

          ![image-20221101004226012](.assets/readme.zh/image-20221101004226012.png)
