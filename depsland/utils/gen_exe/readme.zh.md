# 来源

该包使用了以下开源项目/工具:

- [gen-exe](https://pypi.org/project/gen-exe/): 用于将 bat 文件转换为 exe 文件.
- [rcedit](https://github.com/electron/rcedit): 用于修改 exe 文件的属性, 例如替换图标, 添加管理员执行权限等.

# 使用

```py
from gen_exe import bat_2_exe, add_icon_to_exe, elevate_privilege

bat_2_exe('test.bat', 'test.exe')
add_icon_to_exe('test.exe', 'test.ico')
elevate_privilege('test.exe')

# 或者, 向 bat_2_exe 传递更多参数, 包含对后面两个函数的调用.
bat_2_exe(
    file_i='test.bat',
    file_o='test.exe',
    icon='test.ico',
    show_console=True,
    uac_admin=True,
    remove_bat=False,  # remove bat if exe generation succeeds.
)
```

# 为什么写这个包

为什么不直接用 gen-exe:

1. 依赖了 pywin32, 体积有点大, 而且仅能在 windows 下安装 (但我需要在多个系统上工作).
2. 依赖了 click, 但本项目用不到 (本项目用的是另一个命令行工具).
3. 我只用到了一部分函数, 所以想把它的方法提炼并简化一下.

为什么使用 rcedit:

1. 它可以提升执行权限, 这样在客户机上能够正常使用 depsland 的功能.
2. 它非常小, 只有 1.2mb, 我想把它打包进 depsland 的 whl 文件中.

但注意, rcedit 是一个 exe 文件, 仅能在 windows 下使用.

TODO: 我正在考虑通过 poetry 配置, 分开生成 windows 和 macos 的安装包 (rcedit 文件只会在 windows 平台出现), 以适当减少 macos 的安装体积.

# 参考

- https://stackoverflow.com/questions/1022449/how-to-change-an-executables-properties-windows
- https://www.zhihu.com/question/27895048
