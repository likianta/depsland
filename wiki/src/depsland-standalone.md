# 打包 Depsland 为独立应用

## 前置检查

- [ ] 确认 pyproject.toml 和 poetry.lock 已同步
- [ ] 配置环境变量: ...

## 打包

帮助命令:

```sh
python build/build_depsland/main.py -h
python build/build_depsland/main.py main -h
```

常用打包命令:

- `python build/build_depsland/main.py main -z -u`

    说明: 打包 (生成目标文件夹) + 压缩 (到 .7z 文件) + 上传 (将 .7z 上传到 aliyun oss).

    效果:

    - pyproject.toml 版本号自动 bump 一次
    - 生成 `dist/standalone/depsland-$version` 文件夹
    - 生成 `dist/standalone/depsland-$version.7z` 文件
    - 软链接上述文件到 resources/depsland.7z 文件 (注意剔除了版本号)
    - 文件上传到 oss:/likianta-public-share/depsland-resources/depsland.7z (注意剔除了版本号)
    
    打包完成后, 请思考: 新的版本是否解决了某些关键问题? 我们是否强烈地需要用户使用我们的新版本? (这意味着旧版本存在着某些不可忍受的显著问题.)

    如果答案为 "是", 那么请检查下面这些位置的代码, 将版本号钉到最新:

    - `depsland/gui/setup_wizard/depsland_installer_online.py:State.depsland_version`
    - `depsland/gui/setup_wizard/depsland_installer_online.py:State.__version__`
    - `sidework/mini_launcher/app_launcher.v:check_version_of_installed_depsland:$some_comment`
    - `sidework/mini_launcher/app_launcher.v:check_version_of_installed_depsland:$some_code_case`

- `python build/build_depsland/main.py main -p full`

    说明: 只生成 `dist/standalone/depsland-$version` 文件夹, 但不生成 7z 文件, 也不上传到 oss.

    该命令是所有参数组合中, 运行最快的. 适合本地调试, 比如, 当我们想要测试双击 Depsland.exe 会不会报错时, 会用这种方式生成 `depsland-$version` 文件夹, 然后双击下面的 Depsland.exe 看看能否启动成功.

    注意: 如果结果经测试没有问题, 不要直接对这个文件夹压缩后上传! 你应该重新跑一下 `python build/build_depsland/main.py main -z -u`.

    附: 常见的错误原因:

    - 因更新依赖导致 tree-shaking 没有覆盖缺失的依赖, 导致启动时报 `ModuleNotFoundError`.
    - 某些依赖删除了 (比如 `lk-logger`), 但是旧代码中仍然在使用它 (没有清理干净).

## 其他命令

如果只想 bump 版本, 其他不改变, 请不要直接手动修改 `pyproject.toml:project:version`, 而应该用下面的命令:

```sh
# a. 自动 bump 最末位的版本号
python build/build_depsland/main.py bump_version

# b. 手动指定新的版本号 (示例)
python build/build_depsland/main.py bump_version 0.13.0
#   如果手动指定的版本号低于当前项目版本号, 会报错.
```

它会更新:

- `pyproject.toml:project:version`
- `depsland/__init__.py:__version__`
- *未来可能会加入更多地方...*

## 下一步

...