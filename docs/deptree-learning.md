deptree 模块背景知识学习
========================

# importlib.metadata

`importlib.metadata` 是内置模块.

## Context

`Context` 指的是 `importlib.metadata.DistributionFinder.Context`.

关键变量:

```
metadata.DistributionFinder.Context.__init__:kwargs
    path: list[str]. 默认为 `sys.path`. 您可以传入一个特定的路径, 以限定 Python 
        包的查找范围.
    name: Optional[str]. 默认为 None.
        当为 None 时, 表示获取 path 下所有的包.
        当为特定的名字时, 则尝试查找与该名字匹配的包.
`Context.__init__:kwargs` 将被更新到 `Context.__vars__` 中.
```

示例:

```python
from importlib import metadata

context = metadata.DistributionFinder.Context(
    path=['D:/my_proj/venv/lib/site-packages'],
    name=None,
)

# 因为 `context:vars:name` 是 None, 所以将获取到 `context:vars:path` 下的所有包
# 列表.
# 如果 `context:vars:name` 不为 None, 且不存在, 则报 `PackageNotFoundError`.
for d in metadata.Distribution.discover(context=context):
    #   type(d): metadata.PathDistribution
    pass

```

## 获取指定目录下的所有包列表

假设有目录:

```
|= D:/my_proj/venv/lib/site-packages
    |= idna
    |= idna-2.10.dist-info
    |= requests
    |= requests-2.25.1.dist-info
    |= urllib3
    |= urllib3-1.26.4.dist-info
```

我们想获取 'site-packages' 目录下的所有包的列表.

```python
from importlib import metadata

def list_all_packages(path) -> list[metadata.PathDistribution]:
    context = metadata.DistributionFinder.Context(path=path)
    return list(metadata.Distribution.discover(context=context))

```

更丰富的实现请参考 `depsland/main.py:list_all_packages`.



