# 关于本目录

本目录是用于 depsland 项目作为独立版应用发布的一部分.

本目录与 `~/pypi` 有着一致的结构, 但只包含与 depsland 依赖有关的文件.

## 目录结构

当你第一次克隆该项目时, 你将得到以下结构:

```
depsland
|= build
   |- self_build.py  # 这是后面要用到的初始化脚本
|= chore
   |= custom_packages  # 暂时是空目录
|= pypi  # 这些都是空目录
   |= cache
   |= index
   |= downloads
   |= installed
|= pypi_self  # 这些也都是空目录, 且与 `pypi` 结构相同
   |= cache
   |= index
   |= downloads
   |= installed
|= ...
|- requirements.txt   # depsland 的依赖清单
|- ...
```

根据 depsland 的依赖清单 (requirements.txt), 依赖分为两大类:

- 从 pypi 官方站点可下载的依赖包
- (暂时) 无法从 pypi 官方站点下载的自建包 (同样是 whl 文件, 只是由于开发进度等原因没有上传到 pypi)

对于后者, 我们需要从特定的渠道获取它们, 然后放在 `~/chore/custom_packages` 目录.

以 "qmlease>=3.1.0a15" 为例, 我们需要通过克隆 [qmlease](https://github.com/likianta/qmlease) 项目, 更新它的 pyproject.toml 文件, 并在本地使用 `poetry build -f wheel` 生成一个 "qmlease-3.1.0a15-py3-none-any.whl" 依赖包, 将它放在 `~/chore/custom_packages` 目录下.

请逐一确认有哪些是自建依赖包, 在全部放到`~/chore/custom_packages` 目录后, 开始下一步:

## 初始化 index 文件

在项目初始, 我们的 `~/pypi/index` 和 `~/pypi_self/index` 目录都是空的.

我们需要通过脚本来创建初始的文件:

```shell
# 获取帮助
py build/self_build.py -h
# 初始化 `~/pypi/index`
py build/self_build.py init pypi
# 初始化 `~/pypi_self/index`
py build/self_build.py init pypi_self
```

## 下载和构建 depsland 依赖环境

```shell
# 获取帮助
py build/self_build.py build -h
# 根据 depsland 的 requirements.txt 文件构建 pypi 目录
py build/self_build.py build
```

注意这一步的时间耗时很长, 因为涉及到下载 pyside6 等大体积的依赖.

该过程主要分为三部分:

1. 下载依赖包, 这些依赖会被下载到 `~/pypi_self/downloads` 目录.
2. 安装依赖包, 这些安装结果在 `~/pypi_self/installed` 目录.
3. 构建依赖树, 它们会刷新 `~/pypi_self/index` 下的文件.

**注意事项**

- 如果你已经下载过依赖了, 即 `~/pypi_self/downloads` 目录不为空, 请传入 `-sd` 跳过下载步骤. 即:

    ```shell
    py build/self_build.py build -sd
    ```

- 如果你已经安装过这些依赖, 即 `~/pypi_self/installed` 目录不为空, 请传入 `-si` 跳过安装步骤. 即:

    ```shell
    py build/self_build.py build -sd -si
    ```

- 如果你想要重新构建依赖树, 请输入:

    ```shell
    py build/self_build.py build -sd -si
    ```

    (ps: 和上个命令相同.)

    特别是, 如果你不慎地二次调用了 `py build/self_build.py init pypi_self` 导致 index 被重置, 请运行上述命令让它刷新构建.

考虑到未来我们仍然会不定期地更新 depsland 的依赖清单, 你有两种方法来重新构建依赖树:

- 使用 `py build/self_build.py build` 进行完整的构建, 脚本会自动跳过已经下载过的库, 所以时间仍然可以让人接受.
- 手动通过命令行完成 `pip download` 和 `pip install` 过程, 再调用 `py build/self_build.py build -sd -si`.

第二个方法比第一个速度更快一些.

另外需注意, 对于依赖的升级, 裁剪操作, 无法用 `~/build/self_build.py` 脚本完成. 你需要人工介入, 手动删除 downloads, installed 下面多余的文件和目录, 并运行 `py build/self_build.py build -sd -si` 刷新依赖树.

## 将依赖软链接到 python site-packages

> 在开始本节之前, 你应完成 `~/python/README.zh.md` 所描述的工作.

输入以下命令:

```shell
py build/self_build.py link
```

它会将 `~/pypi_self/installed` 中的资源软链接到 `~/python/Lib/site-packages` 目录.

注意: 对于依赖的裁剪操作, 你需要手动完成软链接的解除.
