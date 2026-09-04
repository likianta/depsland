# Depsland 项目概要

## 这是什么项目

本项目为其他 Python 项目提供 "打包 - 发布 - 下载" 工具链. 你可以将自己的 Python 项目包装成一个 ".zip" 或 ".exe" 单文件, 并具备可控的初始体积和快速的增量更新策略.

Depsland 通过配置文件来管理一个项目该如何打包. 你也可以通过 Depsland GUI 来管理每个项目, 整个流程既可以通过 CLI 完成, 也可以 GUI 完成.

## 项目目录结构

- `.venv`: 本项目的 Python 虚拟环境, 使用 uv 创建. Python 版本为 3.12.
- `apps`: Depsland 会将已打包的项目的信息, 数据资产, 配置文件等存储在这里.
  - `apps/<appid>`: 在 apps 目录下, 每个项目有独立的目录.
  - `apps/<appid>/<version>`: 每个打包的项目的每个版本有独立的目录.
- `build`: 构建自身项目的一些脚本和资产 (启动器图标, 启动器源代码, 项目自检程序等).
  - `build/exe/check_updates.v`: 使用 V 语言编写的检查更新工具. 实际上这是一个补丁工具.
- `depsland`: 项目的源代码.
  - `depsland/api`: 核心接口.
    - `depsland/api/dev_api`: 开发者相关的核心接口, 例如打包, 发布.
    - `depsland/api/self_api`: 自身相关的核心接口, 例如自身升级.
    - `depsland/api/user_api`: 用户相关的核心接口, 例如下载安装应用, 运行应用.
  - `depsland/depsolver`:

    处理复杂的依赖关系, 将它们最终转化为展平的 (没有嵌套关系的) PackageInfo 对象 (参考 `depsland/depsolver/uv_lock_resolver.py:T:PackageInfo`).

    目前我们主要使用基于 uv.lock 的 `depsland/depsolver/uv_lock_resolver.py` 处理器.

  - `depsland/gui`: 可视化界面. 分为几个部分: 应用构建器, 应用管理器, 应用商店, 在线补丁制作器, 安装向导.
  - `depsland/manifest`: 应用清单解析和导出.

    Depsland 使用 "清单" 管理其他项目的打包细节. 清单的原始文件是一个 JSON 文件. 我们的 `manifest` 模块用来解析和返回一个 Manifest 对象.

    清单的主结构参考 `depsland/manifest/typing.py:T:Manifest1`.

  - `depsland/normalization`: 用于格式化杂乱的依赖包名称, 统一版本号形式, 使 SemVer 规范可以继续处理它们.
  - `depsland/oss`: 完成资产文件上传/下载.
  - `depsland/paths`: 由于项目牵涉的路径非常多而且复杂, 我们使用 paths 模块来统一管理.
  - `depsland/platform`: 创建平台相关的启动器.
  - `depsland/pypi`: 加载已缓存的依赖包, 更新依赖列表, 复用本地依赖.

- `pypi`: Depsland 会自己管理所有项目的依赖包. 类似于 uv cache, poetry cache 的设计目的.
- `run`: 这是一个目录, 里面包含了很多一行 CLI 可搞定的常用命令.
- `sidework`: 周边工作, 例如转换图标格式, 迷你启动器, BAT 转 EXE 工具等.
- `test`: 当需要测试和验证一些功能时, 会在这里创建测试脚本.
- `wiki/src`: 项目使用说明和开发文档都放在这里.
- `pyproject.toml`: 我们使用现代的 Python 项目管理方式 (uv + ruff + ty).

## 工具链

- 使用 `uv run python` 或者 `.venv/Scripts/python.exe` 运行脚本. (注意不要直接用 `python` 这个全局命令.)
- 使用 `uv` 管理 pyproject.toml 中的依赖.
- 使用 `ty` 检查类型错误.
- 使用 `ruff` 格式化代码.

## 代码风格

- 优先使用 `format` 而不是 `f-string`.
- 代码中使用全英文, 不要有中文注释.
- 不需要在入口脚本的顶部添加 `sys.path.append(...)`. 因为我们已经设置好了环境变量 (`PYTHONPATH=.;src;lib;.venv/Lib/site-packages`).
- 每行代码不超过 80 字符 (见 `pyproject.toml:[tool.ruff]:line-length`).
- 每当完成修改后, 使用 `ty check`, `ruff check`, `ruff format` 等命令检查代码风格.
