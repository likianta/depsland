
[## 构建流程]

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
