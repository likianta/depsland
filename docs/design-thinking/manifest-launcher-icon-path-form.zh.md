# 关于清单中的启动器图标的路径问题备忘

在一开始的设计中 (v0.8.2 以前), 我们在清单中定义的启动器图标的路径是一个相对路径.

在程序内部的整个处理周期中, 它也一直以相对路径的形式存在.

于是我们在使用时, 会有如下的代码 (示意):

```python
...
if x := manifest['launcher']['icon']:
    icon_path = '{}/{}'.format(manifest['start_directory'], x)
    create_launcher(
        ...,
        icon=icon_path
    )
```

上面的代码是用来在必要时, 将相对路径转换为绝对路径, 以添加启动器图标.

值得一提的是, 相对路径不是我们想要的形式. 我们希望在程序内部的整个处理周期中, 清单中所有的路径都必须是绝对路径, 因为这样可以减少心智负担, 不必时时刻刻提防着 "相对路径 - 绝对路径" 转化的问题.

但是启动器图标的路径想要改成使用相对路径, 其实遇到了一些困难, 所以直到 0.8.2 版本才着手解决它.

**Q: 什么样的困难?**

创建启动器图标的操作是程序末期的工作, 而绝对路径的形成, 是程序前期的工作.

在前期到后期之间的流程, 我们会有一些操作, 调整清单的根目录路径.

调整根目录是危险的操作, 因为它会导致前期固化的绝对路径, 基本都会失效.

而我们之所以没有遇到大面积的绝对路径失效问题, 只是在启动器图标这一环节才发现, 一方面是运气好 -- 因为我们大部分跟路径有关的操作都集中在中期, 另一方面是我们在设计时就已经谨慎考虑切换根目录的时机及必要性等细节问题.

只可惜切换根目录的时机恰好在创建启动器之前, 所以绝对路径的问题单独在启动器环节显露了.

在 0.8.3 版本中, 我们排查了二者的冲突. 最终得到解决.

相关改动见以下位置:

- `depsland/manifest/manifest.py`
  - `[class] Manifest`
    - `[prop-set] start_directory`
    - `load_from_file`
    - `dump_to_file`
- ...
