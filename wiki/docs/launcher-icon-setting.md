# 如何设置启动器图标

不同平台要求的图标格式不同. 请根据你的平台选择:

| 平台 | 图标格式 |
| ---- | -------- |
| linux | .png |
| macos | .icns |
| windows | .ico |

如果未指定图标, 则会使用 depsland 默认的图标. 它位于 `build/icon` 目录.

如果要适配全平台, 下面是一个示范做法来生成所有格式:

1. 制作你的启动器图标. 或者, 从 [macosicons](https://macosicons.com/), github (例如 [zabriskije 的作品](https://github.com/Zabriskije/macOS-Icons)) 等网站寻找一个合适的图标.

    > macosicons 网站提供的是 bigsur 风格的图标, **icns 格式**. 我们将以此格式为例讲解如何生成其他格式.

2. 打开命令行, cd 到本项目, 执行以下命令:

    ```sh
    # 请确保你的 python 环境已安装 pyproject.toml 或者 poetry.lock 中的依赖.

    # 获取帮助
    python sidework/image_converter.py -h

    # 将 icns 转换为 png 和 ico
    python sidework/image_converter.py all /path/to/your/launcher.icns
    #   它会在 "launcher.icns" 的同一目录下生成结果.

    # 你也可以只转换为 png 或 ico, 以及互相转换 (部分支持)
    python sidework/image_converter.py icns-2-png /path/to/your/launcher.icns
    python sidework/image_converter.py icns-2-ico /path/to/your/launcher.icns
    python sidework/image_converter.py png-2-ico /path/to/your/launcher.png
    # ...
    ```
