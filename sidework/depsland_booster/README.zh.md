# Depsland Booster

## 这个项目用来做什么?

面向用户提供一个可执行文件, 并带有个性化的启动器图标.

面向开发者提供一个稳定可靠的传参方式, 在启动时调用软件根目录下的同名的 bat 脚本, 间接地完成传参.

## 为什么会有这个项目

在 depsland 0.3.6 开发过程中, 我们发现含有空格的参数会在传递到 depsland.exe 时分割错误.

例如:

```sh
depsland run depsland-testsuit check-args aaa bbb "ccc ddd"
```

我们期望得到的参数是 `['aaa', 'bbb', 'ccc ddd']` , 但是实际上得到的是 `['aaa', 'bbb', 'ccc', 'ddd']` (ccc 和 ddd 被拆开了).

经过调查, 该 bug 是由 gen-exe 模块引起的. 我们不得不换一种方式来生成 depsland.exe.

下面是我们拟定的几个方案:

- 参考 poetry 创建可执行程序 (在 python scripts 目录下生成 exe 文件) 的方式, 有希望通过它来创建一个能够正常处理传参的 exe 文件.
- 不再使用 exe, 而是改用 bat -> link + icon 的形式.
- 阅读 gen-exe 作者的源代码, 以及其他人用过它的项目的话, 有没有找到解决方案.
- 寻找新的 bat 2 exe 命令行工具 (例如 [这个](https://github.com/islamadel/bat2exe)).
- 使用 powershell 转 exe 的工具 (ps2exe).

我们对其中一部分展开了测试, 并最终采用了第一个.

这就是 depsland-booster 这个项目的由来.
