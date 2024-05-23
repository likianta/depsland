"""
# 测试 depsland 是否能安装到有空格的本地路径

1. 安装 depsland.
    1. 安装时, 询问安装到哪里, 找一个含有空格的路径.
2. 安装完成后, 打开终端, 输入 `depsland version`, 看是否能够运行.

# 测试 depsland run 能否正确分割含有空格路径的参数

1. 发布 unittets/depsland_testsuit
2. 安装 depsland_testsuit
3. 测试:

    ```sh
    depsland run depsland_testsuit check-args 111 222 "333 444"
    ```
"""
