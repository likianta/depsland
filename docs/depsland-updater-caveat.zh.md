使用 Depsland Updater 须知:

1. 目标项目需要安装这个依赖 (depsland-updater)
2. 目标项目的入口脚本, 需要导入它

    不需要真的执行, 写一段 "死代码" (dead code) 即可.

    例如:

    ```python
    import depsland_updater  # import but not used  # noqa

    def main():
        print('Hello World!')
        ...

    if __name__ == '__main__':
        main()
    ```

    为什么?

    Tree shaking 在裁剪依赖时, 会解析 AST, 显式导入才能触发 tree shaking 包含它.

未来的打算:

让 Depsland 构建/打包器来处理 depsland-updater 依赖, 比如强制包含; 或者用 V 写一个启动器, 当它检测到本地不存在 depsland-updater 时, 在线拉取它.
