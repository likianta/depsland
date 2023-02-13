# 当多个 name-ids 下有重复的 dirnames 时该如何合并

我们使用的策略叫做 "争议-选举": 针对所有有争议的节点, 每个声称对其有所有权的人, 分别提供其在该节点下的 "资产表", 并对资产表中的争议节点进行进一步的 "争议-选举", 直到所有争议节点都被解决.

模拟流程如下:

1. 仲裁方检视每个 name-id 的根目录名列表, 从中找到重复的目录名, 将其记录下来, 作为下一步的争议话题的开端.
2. 首先提出第一个争议目录 A:
    1. 此时, B, C, D 都表示自己有 A 这个目录的所有权.
    2. 仲裁方检视 B C D 每个人在 A 下的具体资产情况, 从中找到重复的资产名, 将其记录下来, 作为该争议的其中一个子话题.
        1. 如果有重复的资产名:
            1. 从这些有争议的资产中, 提出第一个争议节点 E:
                1. 如果 E 是一个 "文件" 类型, 则以最先声明的人为准 (这样设计是顺序相关的, 因此请不要在选举之前对 name-ids 进行任何排序操作). 同时, 以 log 的形式通知开发者.
                2. 如果 E 是一个 "文件夹" 类型, 则重复上述过程, 直到所有争议节点都被解决.
        2. 如果没有, 则每个提交资产的人, 都有权在该目录下创建各自声明的资产.

最终我们得到的是一个这样的数据结构:

```py
dict[str relpath, str name_id]
```

示例:

```py
{
    'bin/pip.exe': 'pip-22.0.2',
    'bin/poetry.exe': 'poetry-1.2.0',
    'bin/ipython.exe': 'ipython-8.6.0',
    'bin/ipython3.exe': 'ipython-8.6.0',
    ...
    'PySide6/__init__.py': 'pyside6-6.4.0',
    'PySide6/examples/axcontainer': 'pyside6_addons-6.4.0',
    'PySide6/examples/corelib': 'pyside6_essentials-6.4.0',
    ...
}
```