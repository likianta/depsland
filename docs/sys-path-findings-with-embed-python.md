关于嵌入式 Python 与模块路径查找 (`sys.path`) 有关的问题的研究
==============================================================

这篇文章的前置知识是: 

**嵌入式 Python 在命令行运行脚本时, 和通过标准方法安装的 Python 运行脚本时的 `sys.path` 是不同的.**

嵌入式 Python 运行时的 `sys.path` 缺少很多关键的目录 (如 '脚本所在的目录', Pycharm 向里面自动添加的目录等), 这就导致原本通过标准安装的 Python 能调用正常的脚本, 在嵌入式 Python 中出现了 `import` 语句的各种 `ModuleNotFound` 错误.

本文旨在探究该问题产生的原因, 以及应对措施.

[相关成果](#20210620164821) 已经在 `depsland` 项目中得到落实.

# Embed Python "._pth" 文件的作用

当我们下载了 embed python 后, 解压到本地:

```
example
|= python-3.9.5-embed-amd64
    |- python.exe
    |- python.zip
    |- python39._pth
    |- ...
```

注意这里有一个 "python39._pth" 文件.

用记事本打开它:

```
python39.zip
.

# Uncomment to run site.main() automatically
#import site

```

该文件将影响 embed python 的模块路径查找 -- 也就是 `sys.path` -- 的行为.

**示例**

注: 您可以跳过此示例, 直接看下一节点 ["结论"](#20210620154627).

假设我们新建一个 "main.py" 的文件, 目录结构和示例代码如下:

```
example
|= python-3.9.5-embed-amd64
    |- python.exe
    |- python39._pth
    |- ...
|= my_script
    |- main.py ::
    |       # 里面只有两行简单的测试代码
    |       import sys
    |       print(sys.path)
```

打开 cmd, 输入 (注意: 把示例中的波浪线替换为您电脑上的实际路径):

```
~/example/python-3.9.5-embed-amd64/python.exe  ~/my_script/main.py
```

可以看到:

```py
['~\\example\\python-3.9.5-embed-amd64\\python39.zip',
 '~\\example\\python-3.9.5-embed-amd64']
```

<span id="20210620154627">**结论**</span>

在 "python39._pth" 文件中定义的路径, 会作为 `sys.path` 的搜索路径. 默认情况下, **embed python 只会将其所在的目录以及其目录下的 `python39.zip` 中的标准库加载到 `sys.path`**.

# 向 "python39._pth" 文件添加自定义路径

假设我们想要把 'scripts' 和 'lib/site-packages' 也加入进去, 可以这样做:

```
example
|= scripts: 假设 scripts 和 lib/site-packages 位于 python.exe 的上级目录
    |- pip.exe
    |- pip3.exe
    |- pip3.9.exe
|= lib
    |= site-packages
        |= pip
        |= pip-21.1.2.dist-info
        |= setuptools
        |= setuptools-57.0.0.dist-info
|= python-3.9.5-embed-amd64
    |- python.exe
    |- python.zip
    |- python39._pth ::
    |       # 我们在此文件中应该这样修改...
    |       python39.zip
    |       .
    |       ../scripts  # 注意这里
    |       ../lib/site-packages  # 还有这里
    |       
    |       # Uncomment to run site.main() automatically
    |       #import site
    |- ...
|= my_script
    |- main.py ::
    |       # 里面只有两行简单的测试代码
    |       import sys
    |       print(sys.path)
```

再次在 cmd 中测试:

```
~/example/python-3.9.5-embed-amd64/python.exe  ~/my_script/main.py
```

可以看到:

```py
['~\\example\\python-3.9.5-embed-amd64\\python39.zip',
 '~\\example\\python-3.9.5-embed-amd64',
 '~\\example\\python-3.9.5-embed-amd64\\../scripts',
 '~\\example\\python-3.9.5-embed-amd64\\../lib/site-packages']
```

显然, 路径的写法存在一些问题, 我们把 `#import site` 那一行取消注释, 变为 `import site`. 再试一次, 会发现正常了:

```py
['~\\example\\python-3.9.5-embed-amd64\\python39.zip',
 '~\\example\\python-3.9.5-embed-amd64',
 '~\\example\\scripts',
 '~\\example\\lib\\site-packages']
```

到此为止, 我们知道了如何向 "python39._pth" 添加自定义路径. 这有助于我们在使用嵌入式 Python 时, 向 `sys.path` 加入第三库路径.

# 怎么加入 '脚本所在的目录'

上一章节没有解决 "怎么加入 '脚本所在的目录'" 这个问题. 因为我们不知道怎么在 "python39._pth" 中表示.

事实上, 笔者也没有找到有效的方法. 但我们另辟蹊径, 把 "python39._pth" 删除后, 就会有新的发现:

```py
['~\\example\\my_script',  # <- new (1)
 '~\\example\\python-3.9.5-embed-amd64\\DLLs',  # <- new (2)
 '~\\example\\python-3.9.5-embed-amd64\\lib',  # <- new (3)
 '~\\example\\python-3.9.5-embed-amd64\\python39.zip',
 '~\\example\\python-3.9.5-embed-amd64']
```

`sys.path` 多出了三个路径, 而且更重要的是, '脚本所在的目录' 也被加入进去了.

# 最终解决方案

其实删除了 "python39._pth" 文件后的 embed python, 其模块搜索路径与标准安装的 python 是基本没有差别的.

那么还有一个问题, 以前我们创建的标准的 venv 的目录结构是这样的:

```
hello_world_project
|= ...
|= venv
    |= Include
    |= Lib
        |= site-packages
            |= ...
    |= Scripts
        |- pip.exe
        |- pip3.exe
        |- pip3.9.exe
        |- python.exe
        |- pythonw.exe
        |- ...
    |- pyvenv.cfg
```

embed python 也能实现吗? 答案是肯定的. 只是目录结构需要一些调整:

```
hello_world_project
|= venv_based_on_embed_python
    |- python.exe       : 将之前的 'python-3.9.5-embed-amd64' 下的内容放到了这里
    |- pythonw.exe
    |- python.zip
    |                   : 注意从中删除了 "python39._pth" 文件
    |- ...
    |= scripts          : 创建一个名为 "scripts" 的目录
        |- pip.exe
        |- pip3.exe
        |- pip3.9.exe
        |- ...
    |= lib
        |= site-packages
            |= ...
|= src
    |- main.py ::
    |       import sys
    |       print(sys.path)
```

在 Pycharm 中调用, 看到的结果与标准 venv 的结果是一样的:

(注: 笔者的 'site-packages' 中添加了很多库, 所以下面出现了很多额外的路径, 可能是您电脑上没有的; 但就效果而已, 与标准 venv 的结果仍是一样的.)

```py
['~\\hello_world_project\\src',
 '~\\hello_world_project',
 '~\\Pycharm 2021.1\\plugins\\python\\helpers\\pycharm_display',
 '~\\hello_world_project\\venv_based_on_embed_python\\python39.zip',
 '~\\hello_world_project\\venv_based_on_embed_python\\DLLs',
 '~\\hello_world_project\\venv_based_on_embed_python\\lib',
 '~\\hello_world_project\\venv_based_on_embed_python',
 '~\\hello_world_project\\venv_based_on_embed_python\\lib\\site-packages',
 '~\\Pycharm 2021.1\\plugins\\python\\helpers\\pycharm_matplotlib_backend']
```

给 embed python 安装 [pip](https://pip.pypa.io/en/stable/installing) 后, 在 Pycharm - Settings - Project Interpreter 中也可以显示:

![](.assets/20210620_172946.png)

# 备注

<span id="20210620164821"></span>

Depsland 创建的 venv 目录结构见 [project-structure.md](./project-structure.md).
