# 打包 Depsland 为独立应用

## 前置检查

- [ ] 确认 pyproject.toml 和 poetry.lock 已同步
- [ ] 配置环境变量: ...

## 打包

命令:

```sh
# 获取帮助
python build/build_depsland/main.py -h
python build/build_depsland/main.py main -h

# 常用命令:
# 打包 (生成目标文件夹) + 压缩 (到 .7z 文件) + 上传 (将 .7z 上传到 aliyun oss)
python build/build_depsland/main.py main -z -u
#   效果:
#   - pyproject.toml 版本号自动 bump 一次
#   - 生成 dist/standalone/depsland-<version> 文件夹
#   - 生成 dist/standalone/depsland-<version>.7z 文件
#   - 软链接上述文件到 resources/depsland.7z 文件 (注意剔除了版本号)
#   - 文件上传到 oss:/likianta-public-share/depsland-resources/depsland.7z (注意剔除了版本号)
```

打包完成后, 请思考: 新的版本是否解决了某些关键问题? 我们是否强烈地需要用户使用我们的新版本? (这意味着旧版本存在着某些不可忍受的显著问题.)

如果答案为 "是", 那么请检查下面这些位置的代码, 将版本号钉到最新:

- `depsland/gui/setup_wizard/depsland_installer_online.py:State.depsland_version`
- `depsland/gui/setup_wizard/depsland_installer_online.py:State.__version__`
- `sidework/mini_launcher/app_launcher.v:check_version_of_installed_depsland:$some_comment`
- `sidework/mini_launcher/app_launcher.v:check_version_of_installed_depsland:$some_code_case`

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