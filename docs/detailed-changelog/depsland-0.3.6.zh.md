# 0.3.6: 修复带空格的路径, 以及管理员权限问题

> 我们会在某些关键的节点, 对正在发布的版本的更新内容进行详细解读, 以方便大家更深入地了解这些努力背后的意义和价值. 这些文章会统一放在 `docs/detailed-changelog` 目录.
>
> 如果你是 depsland 的深度用户, 这些信息将为你接下来考虑是否立刻升级提供参考. 我们希望一些对你有帮助的改善能让你更好地使用 depsland.

## 修复带空格的路径

在上一版本 (0.3.5) 中我们发现, 有两种情况会导致 depsland 解析空格错误:

1. 安装路径中包含空格.

    例如, 我将 depsland 安装在 `C:\Program Files\Depsland` 下, 在启动时, 会报 `Error: Cannot find module 'C:\Program'` 的错误.

2. 传参时, 某个路径参数包含了空格.

    例如 `depsland run reqs_deps_maps "C:\demo\8-6 LV4-xxx", 程序会误认为 `C:\demo\8-6` 和 `LV4-xxx` 一共是两个参数.

关于第一个问题, 我们在代码中发现这是一个比较低级的错误, 原因是启动时的命令中, 忘记给启动路径加上双引号了. 于是我们很快地做了以下修复:

before (~/depsland.exe)

```sh
%DEPSLAND%\python\python.exe -m depsland ...
```

after (~/depsland.exe)

```sh
"%DEPSLAND%\python\python.exe" -m depsland ...
```

而第二个问题则没那么简单.

它是由一个 bat 转 exe 工具产生的, 我们设计了一个单元测试, 将这个现象简化后复现了出来:

```sh
depsland run testsuit check-args aaa bbb "ccc ddd"
#   预期结果: ['aaa', 'bbb', 'ccc ddd']
#   实际结果: ['aaa', 'bbb', 'ccc', 'ddd']
```

初步猜想是 [silvandeleemput (gen-exe 这个库的作者)](https://github.com/silvandeleemput/gen-exe) 的库存在这样的 bug.

我们尝试了几种解决方案:

- 重新寻找一个 bat 转 exe 的工具

    - https://github.com/tokyoneon/B2E

        缺点: 处理速度比较慢 (相对于 gen-exe 几十毫秒来说, 这个工具需要 1 ~ 5 秒钟的时间). 有时候生成不出来图标.

    - https://github.com/islamadel/bat2exe

        缺点: 以文件夹为单位打包成 exe, 不能满足我们的需求.

- 换用 powershell 转 exe 的工具

    - ps2exe: 官方的工具

        问题: `Install-Module` 命令找不到, 工具安装失败.

- 利用 poetry -> python/scripts 机制, 来间接生成一个 exe

    - 问题: 尝试往这个生成的 exe 里面写入新的图标, 会导致启动报错. 此外, 这个 exe 必须配一个 `.<appname>.json` 文件放在同目录下, 无疑增大了部署的成本 (而且不够优雅).

在经历以上尝试和不满意后, 最终我们把目光重新放到 gen-exe 这个库上.

gen-exe 的作者的 github 仓库里同时存放了他生成 exe 模板所用到的 cpp 代码. 虽然本人没有 cpp 的基础, 但是通过一些简单的推测找到了代码的关键部分. 接下来我尝试写了一个简单的 demo 来测试 cpp -> exe 以及传参问题是否被解决. 答案是令人高兴的.

这些工作被放在了 `sidework/bat_2_exe_tempate_gen` 目录下. 在经过短暂的 g++ 编译后, 我们终于得到了一个可以正常工作的 exe.

这个工作跨度两三天的时间, 这也是为什么此次发布比预计的要晚的原因 (从我们的 commit 历史可以看出围绕它做了很多工作).

## 管理员权限

之前我们将默认的安装位置放在了 ProgramData -- 也就是 `C:\ProgramData\Depsland` 的位置.

这个位置的权限问题简单描述为:

- 文件的创建者有所有权.
- 非文件的所有者必须拥有管理员权限才能对文件进行操作.

例如, A 用户在该目录下创建了一个文件, 然后切换到 B 用户登录此台电脑. 虽然 B 用户可以看到这个文件, 但只能以 "只读" 的形式, 如果要编辑, 就要请求管理员权限重新打开.

解决方法比较简单, 我们将默认安装位置改为了 LocalAppData -- `C:\Users\<Username>\AppData\Local\Depsland`.

这个问题的解决对以下用户有帮助:

- 用户想要编辑安装目录下的文件.
- 用户工作在安全功能严格的系统上, 不能获取管理员权限.

## 参考

- gen-exe 项目地址: https://github.com/silvandeleemput/gen-exe
- 其他 b2e 工具/方案:
    - https://github.com/tokyoneon/B2E
    - https://github.com/islamadel/bat2exe
    - https://github.com/electron/rcedit
    - https://github.com/MScholtes/PS2EXE
- cpp 初步学习
    - argc, argv:
        - https://blog.gtwang.org/programming/c-cpp-tutorial-argc-argv-read-command-line-arguments/
        - https://stackoverflow.com/questions/3024197/what-does-int-argc-char-argv-mean
- mingw64 g++ 编译:
    - https://juejin.cn/post/7143280156042330125
    - https://stackoverflow.com/questions/46728353/mingw-w64-whats-the-purpose-of-libgcc-s-seh-dll
- 文件夹与用户权限:
    - https://www.zhihu.com/question/546008367
    - https://stackoverflow.com/questions/22107812/privileges-owner-issue-when-writing-in-c-programdata
    - 通过 exe 提权: https://github.com/electron/rcedit
