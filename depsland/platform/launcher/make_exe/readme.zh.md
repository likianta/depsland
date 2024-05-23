# make_exe 说明

本目录包含了两个子包: `bat_2_exe_1` 和 `bat_2_exe_2`. 这里末尾的 1 和 2 是按照时间顺序命名的, 没有其他特殊含义.

下面我会分别说明 1 和 2 包的功能和特点.

## bat_2_exe_1

### 来源

该包使用了以下开源项目/工具:

- [gen-exe](https://pypi.org/project/gen-exe/): 用于将 bat 文件转换为 exe 文件.
- [rcedit](https://github.com/electron/rcedit): 用于修改 exe 文件的属性, 例如替换图标, 添加管理员执行权限等.

### 使用

用法 1:

```py
from gen_exe.bat_2_exe_1 import bat_2_exe, add_icon_to_exe, elevate_privilege
bat_2_exe('test.bat', 'test.exe')
add_icon_to_exe('test.exe', 'test.ico')
# elevate_privilege('test.exe')
```

用法 2:

```py
# 2 和 1 的功能基本相同, 但是写法更紧凑, 推荐使用 2.
from gen_exe.bat_2_exe_1 import bat_2_exe
bat_2_exe(
    file_i='test.bat',
    file_o='test.exe',
    icon='test.ico',
    show_console=True,
    # uac_admin=True,
    remove_bat=False,  # remove bat if exe generation succeeds.
)
```

### 为什么写这个包

为什么不直接用 gen-exe? -- gen-exe 的缺点:

1. 依赖了 pywin32, 体积有点大, 而且仅能在 windows 下安装 (但我需要在多个系统上工作).
2. 依赖了 click, 但本项目用不到 (本项目用的是另一个命令行工具).
3. 我只用到了一部分函数, 所以想把它的方法提炼并简化一下.

为什么使用 rcedit:

1. ~~它可以提升执行权限, 这样在客户机上能够正常使用 depsland 的功能.~~
2. 它非常小, 只有 1.2mb, 我想把它打包进 depsland 的 whl 文件中.

但注意, rcedit 是一个 exe 文件, 仅能在 windows 下使用.

TODO: 我正在考虑通过 poetry 配置, 分开生成 windows 和 macos 的安装包 (rcedit 文件只会在 windows 平台出现), 以适当减少 macos 的安装体积.

### 注意事项

最近发现使用 rcedit 提升管理员权限会失败, 并且会造成电脑内存压力瞬间暴涨. 因此不再推荐使用本包的 `elevate_privilege` 函数. (我在代码中将它改成了强行触发报错.)

### 参考

- https://stackoverflow.com/questions/1022449/how-to-change-an-executables-properties-windows
- https://www.zhihu.com/question/27895048

## bat_2_exe_2

### 来源

1. https://github.com/tokyoneon/B2E
2. 谷歌搜索 "bat 2 exe converter", 我找到一个下载链接: https://bat-to-exe-converter-x64.en.softonic.com/

解压后, 有如下目录:

```
downloads
|= bat-2-exe-converter
   |= Examples
   |= Portable
      |- Bat_To_Exe_Converter_(x64).exe
      |- ...
   |- Bat_To_Exe_Converter_(Setup).exe
   |- Important-Notice.txt
```

我拷贝了 `bat-2-exe-converter/Portable/Bat_To_Exe_Converter_(x64).exe` 并重命名为 "b2e.exe", 放在了 `bat_2_exe_2` 目录下.

### 使用

...

## 二者对比

- bat_2_exe_1
    - 优点
        - 速度快
        - 简单易用
    - 缺点
        - 如果设置不显示控制台, 但是启动时会有一个窗口一闪而过, 非常影响体验
        - 无法提升执行权限
        - 需要 template.exe 和 rcedit.exe 两个工具
- bat_2_exe_2
    - 优点
        - 稳定
        - 可设置参数丰富
        - 支持提升执行权限
    - 缺点
        - 速度慢 (大约 2 到 5 秒)
        - 设置图标似乎有问题, 有时候会设置失败, 有时候图标仅支持中等大小, 在大缩略图视图下会看着较小

目前我们的方案是, 除了 `~/build/exe/*.bat` 会用到 bat_2_exe_2 外, 其他情况 (主要指在客户端) 用的是 bat_2_exe_1.

用到 bat_2_exe_2 的情景, 一般是不考虑生成速度, 确保能够提权, 或不显示窗口.

用到 bat_2_exe_1 的情景, 对速度敏感, 且一般要求显示控制台窗口.

备注: 推荐多用 bat_2_exe_2, 未来可能会移除 bat_2_exe_1!
