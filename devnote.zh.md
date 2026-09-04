# 开发者须知

## 初始化项目

- 安装工具链
  - uv
  - mdbook
  - aliyun ossutil 2.0

    用于上传资源到阿里云 OSS 以及从云端拉取应用.

    链接: https://help.aliyun.com/document_detail/2786110.html?spm=5176.8465980.console-base_help.100.4e701450oTNtfn

    测试: `ossutil version`

  - vlang 0.5

    用于构建补丁包和迷你启动器.

    链接: ...

    测试: `v version`

  可选:
  - ruff
  - ty

- 创建虚拟环境

  ```sh
  uv venv --python $path_to_global_python_312
  uv sync --no-install-project
  ```

  目前将解释器版本固定到 3.12. 未来会做多版本支持.

- 下载 Python 3.12 独立版

  从官网下载 embed 3.12 版本, 解压到 python 目录, 然后添加下面两个文件:
  - `python/python312._pth`

    ```
    python312.zip
    .
    import site
    ```

  - `python/sitecustomize.py`

    ```py
    # https://github.com/python/cpython/issues/93875#issuecomment-2487890248
    # print('setting up customized site')
    import os
    import sys
    sys.path[0:0] = ['.', 'lib', 'src', '.venv/Lib/site-packages', '.depsland/mini_deps']
    if p := os.environ.get('DEPSLAND_SEARCH_PATHS'):
        sys.path.extend(p.split(os.pathsep))
    ```

- 设置环境变量 (可选, 用于发布应用到云平台)

  ```nu
  $env.DEPSLAND_CONFIG_ROOT = ...
  ```

## 占用端口说明

```yaml
2180: depsland app builder
2181: depsland app manager
2182: depsland app store
2183: depsland setup wizard - frontend
2184: depsland setup wizard - backend
2185: depsland installer online - frontend
2186: depsland installer online - backend transceiver
2187: depsland installer online - default client server
2188: localnet resources
2189: depsland wiki
2190: depsland patch-maker online - frontend
2191: depsland patch-maker online - backend
2192: depsland patch-maker server (listening to incoming clients)
2193: depsland patch-maker client
```

## 预览文档 (静态站点)

```sh
cd wiki
mdbook serve -n 0.0.0.0 -p 3000
```

## 运行命令

> 缩写备注:
>
> ```yaml
> strun: uv run streamlit run --browser.gatherUsageStats false --runner.magicEnabled false --server.headless true --server.port
> ```

- 启动 Depsland GUI

  ```sh
  python -m depsland launch-gui
  ```

## 构建 Depsland 独立版

...

## 补丁服务器

```sh
python run/patch_maker.py launch_gui_and_server --debug
```

### 开发测试流程

1. 主机: 开发者启动 GUI: `strun 2190 depsland/gui/patch_maker_online/app.py -- --developer-mode`
2. 主机: 开发者启动代理服务器: `python depsland/gui/patch_maker_online/server.py mainloop`
3. 虚拟机: 在虚拟机中安装由 depsland 打包的第三方应用 (no-embed-depsland 模式构建产物)
4. 虚拟机: 打开命令行, cd 到应用安装目录, 然后从私有源安装 depsland-udpater
5. 虚拟机: 运行: `python -m depsland_updater patch_online`
6. 主机: 发现已连接的用户: `python depsland/gui/patch_maker_online/server.py list_users`. 可以得到 unique_id 等信息
7. 主机: 浏览器访问 `http://localhost:2190/?uid=<unique_id>` (把刚才获得的 id 代进去)
8. ...

### 创建独立的补丁工具

```sh
python build/build_depsland/standalone.py bump_version $new_version
python -m depsland build depsland_updater/manifest.json -o -D -P
```

生成结果: `depsland_updater/dist/<appid>-<version>`.

## 提升版本

我们手动更新以下位置的版本号, 或者使用脚本来做:

手动修改 (不推荐, 仅作了解):

- `depsland/__init__.py:__version__`
- `depsland_updater/pyproject.toml:project:version`
- `pyproject.toml:project:version`

脚本修改:

```sh
# a. auto-bump least number
python run/version_bump.py
# b. manual assign new version
python run/version_bump.py $new_version
```

## 版本发布节奏

Alpha -> beta -> formal.

示例: 0.12.2a0 -> 0.12.2a1 -> 0.12.2b0 -> 0.12.2b1 -> 0.12.2.

在发布正式版时, 有以下注意事项:

- 确保 pyproject.toml 中的依赖全部升到 PyPI 可用的版本.
- 更新 wiki/src/changelog.md.
- 对于大版本更新 (x.y.0), 需要发布相应的独立版应用, 并推送到 GitHub Releases (目前非必须).

## 杂项

### 减轻 PyCharm 索引压力

如果你在使用 PyCharm 开发本项目, 将以下目录添加到排除索引中:

- apps
- chore
- dist
- oss
- pypi
- python
- temp
- wiki/book
