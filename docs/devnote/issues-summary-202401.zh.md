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
