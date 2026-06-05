[# Depsland 迷你启动器]

[## 目标]

[
    = 单文件可执行文件 (exe 形式)
    = 体积小 (~3mb 最佳; ~6mb 次佳; ~10mb 一般)
    = 编译快 (V 或 Go)
    = 完整的命令行流水线制作, 减少手工步骤
    = 可通过多种形式分享
    = 文件路径无关 (放在任意文件夹下面都可以执行)
    = 启动速度快, 执行过程快
    = 不需要管理员权限
    = 尽量避免被杀毒软件误判
        例如, 该执行器不要有 "download and execute third exe" 的可疑行为.
]

[## 实现思路]

[$flow
    o- 开发者创建迷你启动器
    -> 通过分发渠道 (网盘, 聊天文件, 邮件附件, 优盘等) 交给用户
    -> 用户下载后, 双击执行
        迷你启动器进程:
            o- 检查用户是否安装了 Depsland 主程序
                是: 检查用户是否安装了目标应用
                    是: 检查目标应用版本是否为最新
                        是: 启动目标应用
                            -o 结束
                        否: 下载最新版本的应用
                            -> 启动目标应用
                            -o 结束
                    否: 安装应用
                        -> 启动目标应用
                        -o 结束
                否: 下载 Depsland 在线安装器 (一个 12mb 大小的文件)
                    -> 启动在线安装器
                        在线安装器进程:
                            o- 与公网上的代理服务器取得联系
                            -> 通过公网链接打开一个浏览器网页, 显示 web 用户界面
                            -> 在界面上, 询问用户打算将 Depsland 主程序安装到哪里
                            -> 用户选择位置后, 开始安装 Depsland 主程序
                            -> 配置 Depsland 主程序环境
                            -> 通过 Depsland 主程序安装目标应用, 并将进度同步显示到 web 用户界面
                            -> 关闭 Depsland 在线安装器
                            -> 启动目标应用
                            -o 结束
]

[
    Q:  为什么迷你启动器在找不到主程序时, 不是去下载主程序, 而是下载 "在线安装器"?
    A:  直接下载主程序太慢了, 会让用户长时间停留在控制台界面. (迷你启动器不具备界面框架, 另外, 出于编译体积考虑, 未来是否支持仍未明确.)
        另外我们想询问用户把主程序安装到哪里, 用控制台的 `input` 来交互对普通用户也不友好.
        所以我们需要让用户尽快地离开控制台界面, 来到一个可视化界面的地方继续操作.
        "在线安装器" 的好处是, 一是迷你启动器可以快速下载它 (只有 12MB), 解压它, 然后运行它.
        二是它包含了更丰富的功能, 特别是远程交互功能 (涉及到 socket, os, pickle, eval, import, 是用 Python 写的, 虽然 V 也有可能实现, 但对本人来说难度太高), 用户利用它来连接远端的服务器, 访问 Web UI, 这样就能可视化地选择安装位置, 点击安装按钮, 看到安装的进度条.
        未来可能考虑把 "在线安装器" 的功能也用 V 语言实现, 这样就不需要它了.
        如果加入界面框架后, 编译体积能控制在 5MB 以内, 也会考虑 all-in "迷你启动器 -> 主程序" 两步走策略.
]

[## 构建流程]

[#~ 构建基础设施]

= 编译 Depsland Online Installer

    [$sh
        # 请先配置 [_ devnote.zh.mo:环境配置:ossutil].
        pox sidework/mini_launcher/make.py tree_shaking_depsland_online_installer -m -c -u
        #   -m: 重新压缩依赖库.
        #   -c: 将结果压缩为 ".zip" 文件.
        #   -u: 上传到 OSS.
        #   完整参数含义见源码注解.
    ]

    生成结果位于 [_ resources/depsland_online_installer.zip].
    注意: 如果该文件的体积有明显变化, 更新代码中的有关它的体积的描述: [_ sidework/mini_launcher/app_launcher.v : download_and_extract_depsland_ol : println].

= 编译 Depsland Standalone (Depsland 主程序)
    见 [_ devnote.zh.mo : h2 构建 : h3 构建 Depsland Standalone].

[#~ 构建目标应用的迷你启动器]

假设目标应用是 "Hello World", 它的项目结构如下:

[:tree
    ...
]

构建命令: [
    a. [...]
    b. [$sh
        pox sidework/mini_launcher/make.py create_launcher_from_profile <hello_world_project>/profile.json
    ]
]

[------------------------------------------------------------------------------]
[// 以下内容已过时, 请酌情修改或删除.]

[## 构建方案]

[// 以下方案章节按可用性降序.]

[### 基于 V 的启动器方案]

结构:

[:tree
    <用户下载目录>
    ├─ launcher.exe
    ├─ depsland_online_installer.zip
    └─ depsland_online_installer
       ├─ minideps
       │  └─ ...
       ├─ python
       │  ├─ python.exe
       │  └─ ...
       └─ main.py
]

[#~ 流程描述]

[
    = 确认目标应用发布版本
        [...]
    = 创建目标应用的迷你启动器

        [$sh
            cd sidework/mini_launcher/by_v
            # 查看帮助
            pox make.py create_launcher_from_profile <target_manifest_file>
        ]
        整个构建过程极快. 生成的 exe 文件体积非常小, 大约 3mb.

        [// 以下流程已废弃.
            = 编译 v 到 exe
                [$sh
                    cd sidework/mini_launcher/by_v
                    v app_launcher.v
                ]
                整个过程极快. 在同目录下会生成 "app_launcher.exe" 文件, 体积 ~3mb.
        ]
    = 将生成的 exe 分享给用户
]

[### 基于 Nuitka 的启动器方案]

[
    = 构建 Depsland Online Installer
        [$sh
            cd sidework/mini_launcher/by_nuitka/depsland_online_installer
            por nuitka --onefile --standalone --windows-console-mode=force --output-filename=depsland_online_installer.exe --noinclude-IPython-mode=nofollow main.py
            cp depsland_online_installer.exe ../../../../resources
        ]
    = 构建 General Launcher
        [$sh
            pox sidework/mini_launcher/by_nuitka/factory.py build_general_launcher
        ]
    = 创建目标应用启动器
        [$sh
            # 示例
            pox sidework/mini_launcher/by_nuitka/factory.py create_launcher 'Hello World Example' hello_world_tkinter 0.5.0 `C:\Likianta\temp\2026-04\Hello World Tkinter (Debug) v0.5.0.exe` --show-console
        ]
    = 开通 2188 端口
        [$sh
            py -m http.server -p 2188 -d resources
            <bore> -p 2188 2188
        ]
    = 运行 airmise 中转站
        [$sh
            pox depsland/gui/setup_wizard/depsland_installer_client_support.py start-server
        ]
    = 运行 Streamlit 应用
        [$sh
            strun 2185 depsland/gui/setup_wizard/depsland_installer_online.py
        ]
]

[#~ 问题一览]

[
    Q: 当尝试 [`exec(code)] 时, 会报标准库缺失.
    Q: 当包含第三方库时, 编译时间太长.
    Q: 即使只使用标准库, 编译时间 (~20s) 也不是很理想.
    Q: 体积来到了 6MB, 不太理想.
    Q: 启动速度似乎不是很快.
    Q: 如果使用下载第二个 exe 的方案, 会被杀毒软件误报和拦截.
]

[## 用户访问流程]

[
    = 开发者: 检查或上传资源到 oss

        检查以下资源: [$yaml
            local_entrance: <depsland_project>/resources
            cloud_entrance: <aliyun_oss>/likianta-public-share/depsland-resources
            resource_list:
                - depsland-online-installer.zip
                - depsland-standalone-<version>.zip
        ]
        注意: 目前需要手动上传.

        其中, [depsland-standalone-<version>.zip] 由以下方式创建: [$sh
            pox build/build_depsland/main.py main -z
            cp dist/standalone/depsland-<new_version>.zip resources
            #   mv 命令也可以
        ]

        [depsland-online-installer.zip] 由以下方式创建: 
        [本文 : 章节 : 构建方案 : 基于 V 的启动器方案]

    = 开发者: 运行服务进程
        
        调试环境: [$sh
            pom run start_depsland_online_service <bore_secret> --debug
        ]
        调试环境会占用以下端口: 2185, 2186, 2188.

        生产环境: [$sh
            pom run start_depsland_online_service <bore_secret>
        ]
        生成环境会占用以下端口: 2185, 2186.

    = 用户: 接收到迷你启动器, 双击运行
]
