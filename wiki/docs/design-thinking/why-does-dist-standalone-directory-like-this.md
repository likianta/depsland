# 为什么独立版打包的目录结构要这样设计

目录结构:

```
dist
|- standalone
    |- depsland-0.8.0-windows
        |- depsland
            |- 0.8.0
                |- ...
                |- Depsland.exe
                |- Depsland (Debug).exe
```

这种结构有一个值得注意的点, 那就是 "depsland-0.8.0-windows/depsland/0.8.0". 它看起来像是一种 "冗余" 的结构, 为什么不直接用 "depsland-0.8.0-windows" 这个目录呢?

这是因为我们要为 depsland 的自升级系统做考虑. 在解答上面的问题之前, 我们要先简单解释一下 depsland 的自升级逻辑:

1. 用户从 "depsland-0.8.0-windows/depsland/0.8.0/Depsland.exe" 启动 gui
2. 在 gui 上, 点击自升级按钮, 完成自升级
3. 此时, 会出现以下目录:

    ```
    <user-programs>
    |- depsland
        |- 0.8.0
            |- apps
                |- depsland  # 这是新下载的版本
                    |- 0.9.0
                        |- ...
                        |- Depsland.exe
                        |- Depsland (Debug).exe
            |- ...
    ```

4. depsland (0.8.0) 会执行一个后处理程序, 将新下载的 0.9.0 移动到同级目录, 于是变成了:

    ```
    <user-programs>
    |- depsland
        |- 0.8.0
            |- apps
                |- depsland
                    |- 0.9.0    # 原先的位置
            |- ...
        |- 0.9.0                # 移动到了这里
    ```

5. 然后, depsland 从新的版本创建快捷方式, 覆盖原先的快捷方式

    ```
    <user-programs>
    |- depsland
        |- 0.8.0
        |- 0.9.0
        |- current                  # 一个软连接目录, 原先指向 0.8.0, 现在指向 0.9.0
        |- Depsland.lnk             # <- current/Depsland.exe
        |- Depsland (Debug).lnk     # <- current/Depsland (Debug).exe
    <desktop>
    |- Depsland.lnk         # <- <user-programs>/depsland/current/Depsland.exe
    ```
