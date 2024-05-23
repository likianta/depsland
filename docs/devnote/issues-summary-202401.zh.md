# 近期问题/经验总结 (2024-01)

## python 版本

并不是越新越好. 目前最推荐的是 3.11, 而不是 3.12. 原因是 3.12 只能安装 pyside6 >= 6.6, 而这个版本出现了一些无法解决的难题:

- mixin 与 python 标准的逻辑不符
- 不知道从哪里产生的 `SignalManager ... source::null` 错误
- `engine.addImportPath` 似乎无法正常工作, 导致 qml 中引入自定义的组件库无法识别

我们使用 python 3.11, 对应使用 pyside6 6.4.3 版本. 该版本与 qmlease 契合度最高.

补充: pyside6_lite 是从 pyside6 6.4.3 抽取的, 所以 python 3.12 不能使用.

此外需要注意的是, 切换 python 版本需要重构 pypi 目录. 否则 `pypi/installed` 中会存在混乱的编译版本, `pypi/downloads` 中的包也会进一步污染 `pypi/installed` 中的包.

## 依赖清单

我们主要使用了三种依赖记录格式:

- pyproject.toml
- poetry.lock
- requirements.lock (由 https://github.com/likianta/poetry-extensions 提供支持)

这三种各有利弊:

- pyproject.toml
    1. 没有提供准确的版本锁定
    2. 没有依赖的依赖信息
    2. 提供的原始信息 (主要指 markers) 需要自己去解析, 解析难度过高
- poetry.lock
    1. 和 pypi.index 索引的信息可能对应不上, 导致中途要 fallback 到 pypi.download 和 pypi.install 方法
- requirements.lock
    1. markers 需要自己去处理, 难度过高

目前的方案是以 requirements.lock 为主, 其他作为辅助, 尽量减少 fallback 的几率.

未来我们会以 poetry.lock 作为唯一依据, 围绕它重审整个工作流程.

## 路径长度限制 (windows)

windows 默认的路径长度限制是 260 字符, 在某些情况下会导致应用升级失败.

最近遇到过的案例是, 我们对某个应用使用了 uuid 作为 appid, 这是一个比较长的字符串. 当用户把这个应用解压到一个层级较深的自定义目录后, 用户点击 "Check Updates.exe" 去升级, 会在 `depsland.utils.ziptool.extract_file` 中发生报错.

报错信息是: `FileNotFoundError: ...`, 但实际上是由于某些解压路径超过了 260 字符导致的.

为了解决这个问题, 我们从两方面入手:

1. 不使用长的 uuid 作为 appid, 我们使用较短的随机码 (比如 8 位数)
2. `depsland.utils.ziptool.extract_file` 在 windows 下会给路径加上前缀 `"\\\\?\\"`. 该方法可以有效解决路径长度问题, 目前我们只在这一个地方使用了这个方案, 其他地方 (比如 `os.listdir`, `os.move`) 是否也要这样做, 仍待考虑.
