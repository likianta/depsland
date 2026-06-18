# 我们是如何分析和处理依赖的

依赖位于 `manifest.json:dependencies`, 它支持多种类型 (None, str, dict), 以下详细说明.

## 依赖的类型

### 无依赖

使用 None, 空字符串, 空字典, 都可以表示 "空" 的概念:

```python
# 以下效果相同 (json)
{"dependencies": ""}  # 空字符串
{"dependencies": null}  # 空
{"dependencies": {}}  # 空字典
```

### 从 uv.lock 解析依赖

```json
{"dependencies": "uv"}
```

### 使用树摇技术裁剪依赖

```json5
{
    "dependencies": {
        "method": "tree_shaking",
        "base": "uv.lock", // 可选: 'uv.lock', 'poetry.lock'
        "options": { // 参考 `tree-shaking:/config.py:T.Config0`
            "search_paths": [
                ".",
                ".venv/Lib/site-packages"
            ],
            "entries": [
                "run.py"
            ]
        }
    }
}
```

## 相关代码

- `depsland/manifest/manifest.py:T.Dependencies0`
- `depsland/manifest/manifest.py:Manifest._update_dependencies`

