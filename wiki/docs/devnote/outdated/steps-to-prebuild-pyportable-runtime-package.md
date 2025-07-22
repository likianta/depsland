# 如何预生成一个 "pyportable_runtime" 包

## 预先准备

1.  下载 Microsoft Visual Studio C++ Build Tools, 并安装 "Windows 10 SDK" 和 "C++ 开发工具"
2.  如果本地没有 "pyportable-installer" 项目, 从 github 上克隆一个
3.  在电脑上安装 Python 3.8 (推荐 Python 3.8.10)

## 开始

1.  进入 pyportable-installer 项目目录
2.  运行 `pyportable-installer/sidework/generate_pyportable_crypto_trial_version.py`
    1.  启动函数: `mainloop(key_='we1c0me_to_depsland', auto_move_to_accessory=False)`
        1.  key_ 的值可以改成其他密钥
    2.  在运行过程中, 提示输入系统 python 路径, 粘贴电脑上安装的 Python 3.8 的目录路径
        1.  整个编译时间较长, 大约需要两分钟
    3.  运行完成后, 根据控制台提示, 找到生成的目录, 其格式应如 "pyportable-installer/temp/{random_id}/pyportable_crypto_trial_python38" 所示 (下面简称 "pyportable_crypto_trial_python38")
    4.  将 "~/pyportable_crypto_trial_python38/pyportable_crypto" (目录) 重命名为 "~/pyportable_crypto_trial_python38/pyportable_runtime"
    5.  将 "~/pyportable_crypto_trial_python38/pyportable_runtime" 复制到本项目的 "~/build/pyportable_runtime"

## 下一步

1.  在 "~/build/pyproject.json" 中, 将 `build > compiler > name` 改为 'pyportable_crypto', 以及将 `build > compiler > options > pyportable_crypto > key` 改为 "./pyportable_runtime"
2.  现在, 可以正常运行 `~/depsland/build/build.py` 了
