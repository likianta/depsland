[# Depsland 迷你启动器]

[## 目标]

[
    = 单文件可执行文件 (exe 形式)
    = 体积小 (~3mb 最佳; ~6mb 次佳; ~10mb 一般)
    = 编译快
    = 完整的命令行流水线制作, 减少手工步骤
    = 可通过多种形式分享
    = 启动速度快, 执行过程快
    = 不需要管理员权限
    = 尽量避免被杀毒软件误判
        例如, 该执行器不要有 "download and execute third exe" 的可疑行为.
]

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

[#### 构建流程]

[
    = 编译 v 到 exe
        [$sh
            cd sidework/mini_launcher/by_v
            v app_launcher.v
        ]
        整个过程极快. 在同目录下会生成 "app_launcher.exe" 文件, 体积 ~3mb.
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

[## 问题总结]

[
    Q: 当尝试 [`exec(code)] 时, 会报标准库缺失.
    Q: 当包含第三方库时, 编译时间太长.
    Q: 即使只使用标准库, 编译时间 (~20s) 也不是很理想.
    Q: 体积来到了 6MB, 不太理想.
    Q: 启动速度似乎不是很快.
    Q: 如果使用下载第二个 exe 的方案, 会被杀毒软件误报和拦截.
]
