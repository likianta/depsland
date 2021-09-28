# 如何将 Depsland 与目标应用打包在一起并一键安装?

```
# step1. 分别打包 depsland 和目标应用.
example
|= dist
    |= depsland-v0.1.0-dist.3-win64-full
    |= hello_world_0.1.0-dist.2-full
```

```
# step2. 将 depsland 目录重命名为 "depsland" 并放在目标目录下.
example
|= dist
    |~ depsland-v0.1.0-dist.3-win64-full  ------+
    |= hello_world_0.1.0-dist.2-full            |  # move and rename
        |= depsland  <--------------------------+
```

```
# step3. 将本文所在目录下的 "setup.bat" 复制并覆盖到目标项目的同名文件上.
example
|= dist
    |= hello_world_0.1.0-dist.2-full
        |= depsland
        |- setup.bat  <-----+
depsland-source-project     |
|= build                    |  # copy and override
    |= setup_bundle         |
        |- setup.bat  ------+
        |- bundle-depsland-with-target-app.zh.md  # current article location
```

```
# step4. 现在我们可以把目标应用制作成压缩包了.
example
|= dist
    |= hello_world_0.1.0-dist.2-full  ------+
    |                                       |
    |- hello_world_0.1.0-dist.2-full.zip  <-+
```
