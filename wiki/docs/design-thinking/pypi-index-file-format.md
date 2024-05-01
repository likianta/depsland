# 为什么 `pypi/index` 中的文件格式是 "json" 而不是 "pkl"

在设计中我考虑以下几点:

- `pypi/index` 推荐被设计为可阅读的格式, 尽管这不是必要的
- load/dump 的速度要快, 不过考虑到数据量和使用频度, 这也不是必须的

在本应用的对象结构上来看, pkl 相对于 json 有速度优势; json 比 pkl 有绝对的阅读优势.

所以上面两条是相互冲突的, 我要做的是一个权衡, 而不是一个绝对完美的选项.

最终我选择了 json.

## 影响

该决定将在 2024-05-01 起效, 相关提交见 ...

涉及的主要模块改动:

- `build/init.py : def init_pypi_blank`
- `chore/pypi_blank/index`
- `chore/pypi_self/index`
- `depsland/paths.py : class PyPI`
- `depsland/pypi/index.py`
- `depsland/pypi/insight.py : def rebuild_index`
- `pypi/index`
