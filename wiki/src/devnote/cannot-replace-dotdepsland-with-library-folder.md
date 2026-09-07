# 关于目前无法将 "source/.depsland" 目录改为 "library" 的备忘

"source/.depsland" 在 `manifest:assets` 管辖范围, 我们的 `manifest:dependencies:tree_shaking` 会将依赖以资产的方式添加到 assets list. 而 assets 的格式要求之一是, 资产的路径必须是相对路径 (在当前上下文里, 指的是相对于 "source" 目录), 且不能包含 "../" 开头的路径.

所以本议题搁置, 如果未来要改的话, 依赖和资产的巧妙设计需要被重构.

## 关联代码

- `depsland/manifest/manifest.py:Manifest:_update_dependencies`
- `depsland/depsolver/tree_shaking.py:minify_dependencies`
- `depsland/manifest/assets.py:index_assets`
- `depsland/api/dev_api/build_offline.py:build_offline:dump_manifest`
- `depsland/gui/patch_maker_online.py:air_client:_init_remote_env:get_manifest_data`
