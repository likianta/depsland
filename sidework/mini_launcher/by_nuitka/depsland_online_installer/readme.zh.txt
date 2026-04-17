本模块用于解决 "用户电脑未安装 Depsland" 的情景.

背景: 常规的途径是用户下载迷你启动器, 运行, 迷你启动器检测到用户电脑上已经安装的 Depsland 应用, 然后调用 Depsland 完成后续事情.

如果用户电脑上没安装 Depsland, 而迷你启动器为了体积考虑, 并不具备 "安装 Depsland 的功能". 所以迷你启动器寻求了另一种方法: 首先, 迷你启动器从指定的 url 下载 depsland-online-installer (一个单文件 exe, 体积大约为 20mb), 然后启动后者. 后者会做以下事情:

[
    = 创建一个 Python 进程.
    = 向公网上的 Airmise 进程建立联系, 并得到一个公网端口.
    = 打开用户的浏览器, 访问一个公网地址 (Streamlit 应用), 并在地址中携带上一步拿到的公网端口作为参数.
    = Streamlit 应用是运行在公网服务器上的独立应用, 它会通过上一步拿到的端口参数, 然后建立 [公网 Streamlit <--> 公网端口 <--> 用户端口] 的通讯路径.
    = 接下来, 用户可以通过 UI 来完成 Depsland 的安装以及目标应用的安装.
]

编译: [$sh
    cd <this_directory>
    por nuitka --onefile --standalone --windows-console-mode=force --output-filename=depsland_online_installer.exe --noinclude-IPython-mode=nofollow main.py
]

[// 备忘: 使用精简的 pyproject.toml, 只安装 "airmise\[frp]", "nuitka" 和 "zstandard". 编译出来的体积为 17mb.]

最后, 将 "depsland_online_installer.exe" 复制到 [_ <depsland>/resources/depsland_online_installer.exe].
