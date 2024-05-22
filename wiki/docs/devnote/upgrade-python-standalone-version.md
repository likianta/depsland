# Python 版本升级事项

depsland 独立版会自带一个 python 解释器, 通常我们使用最新版的 python. 例如, 上年用的是 3.11, 今年迁移到了 3.12 版本.

在 3.11 到 3.12 的迁移过程中, 我们发现了一些问题, 并总结了一些经验. 本文作为记录, 以供未来进一步迁移到 3.13 做准备.

## 重建 "pypi" 文件夹

由于 `depsland.pypi` 在记录包信息时, 把 "包名-版本" 作为键存储, 忽略了包的架构等信息. 这会带来一个隐患.

例如, 在 3.11 时期, 我们下载了 "pypi/downloads/numpy-1.26.3-cp311-cp311-win_amd64.whl". 它在 3.12 中不慎被使用的话会导致报错.

做法:

- 手动清理
    1. 重建 "pypi"
        1. 清空 "pypi/downloads" 中的所有文件 (.gitkeep 除外)
        2. 清空 "pypi/installed" 中的所有文件夹 (.gitkeep 除外)
        2. 重新构建 index
    2. 重建 "chore/pypi_self"

        ```sh
        pox ./build/init.py init-pypi-index ./pypi
        ```

- 脚本清理 (推荐)

    ```sh
    pox build/migration.py remove-unsatisfied-whl-files
    pox build/migration.py rebuild-pypi-index
    ```

...
