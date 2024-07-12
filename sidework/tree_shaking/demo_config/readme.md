

```shell
pox -m sidework.tree_shaking batch-dump-module-graphs sidework/tree_shaking/demo_config/modules.yaml
```

```shell
pox -m sidework.tree_shaking make-tree sidework/tree_shaking/demo_config/built_tree.yaml <temp>/depsland_minified
# or: pox -m sidework.tree_shaking make-tree sidework/tree_shaking/demo_config/built_tree.yaml <temp>/depsland_minified --copyfiles
cd <temp>/depsland_minified
mv chore/site_packages lib
py -m depsland -h
py -m depsland launch-gui --port 3001
```
