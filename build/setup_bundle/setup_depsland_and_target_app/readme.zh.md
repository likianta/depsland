# 如何将 Depsland 与目标应用打包在一起并一键安装?

```
# step1. 分别打包 depsland 和目标应用.
example
|= dist
    |= depsland-0.3.2-win64-full
    |= hello_world_0.1.0-dist.2-full
```

```
# step2. 将 depsland 打包结果复制到目标应用根目录下.
example
|= dist
    |= hello_world_0.1.0-dist.2-full
       |= depsland-0.3.2-win64-full  # <- here
```

```
# step3. 将 depsland 文件夹重命名为 'depsland'
example
|= dist
    |= hello_world_0.1.0-dist.2-full
       |= depsland  # <- renamed
```

```
# step4. 将本文所在目录下的 "setup.bat" 复制并覆盖到目标应用根目录的同名文件上.
example
|= dist
    |= hello_world_0.1.0-dist.2-full
        |= depsland
        |- setup.bat  <--------------------------+
                                                 |
depsland-source-project                          |
|= build                                         |  # copy and override
    |= setup_bundle                              |
        |= setup_depsland_and_target_app         |
            |- setup.bat  -----------------------+
            |- readme.zh.md  # current article location
```

```
# step5. 现在我们可以把目标应用制作成压缩包了.
example
|= dist
    |= hello_world_0.1.0-dist.2-full  ------+
    |                                       |  # zip
    |- hello_world_0.1.0-dist.2-full.zip  <-+
```
