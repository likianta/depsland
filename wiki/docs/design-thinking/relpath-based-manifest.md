# 我们应该在 Manifest 类中使用绝对路径吗?

## 结论

不使用.

## 理由

abspath 会导致资产路径和 `depsland.paths` 耦合, 降低了 api 的灵活度.

例如, `depsland.utils.fs.init_target_tree` 支持指定一个入口路径来初始化目标树 (这是一个缺省值). 如果我们使用绝对路径, 这个参数就无法工作.

但并不是所有情况都禁止绝对路径. `depsland.venv.target_venv.indexer.LibraryIndexer.packages:<values>:[key]paths` 是目前已知的唯一一个例外.
