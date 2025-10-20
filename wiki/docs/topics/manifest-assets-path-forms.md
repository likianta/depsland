# 资产清单路径语法格式

## 设计目标

须覆盖情景 (以下用 "x" 指代 "某个"):

- x 目录
- x 目录 (空)
- x 目录下的一级文件
- x 目录下的一级文件以及文件夹 (空)
- x 目录下的所有文件夹 (空)

对于未覆盖到的情况, 比如 "一级文件以及所有文件夹 (空)", 只能通过脚本 (自己编写逻辑) 处理.

## 语法设计

`<path>[:<scheme>]`

- `<path>`

  使用相对路径, 除此之外, **极为有限地** 支持了 `*` 通配符.

- `<scheme>`

  二进制表示法, 有 00, 01, 10, 11 四个值, 其中 00, 01 可以简写为 0 和 1.

  - 00: 创建空的文件夹
  - 01: 仅包含一级文件
  - 10: 包含一级文件和一级文件夹 (空)
  - 11: 所有文件夹 (空)

  Q: 为什么要用二进制, 而不是十进制?

  有助于 "形象化" 地记忆. 例如 "10" 可以理解为 "包含一级文件 (1) 和一级的空文件夹 (0)", 这比数字 "2" 更好记住.

## 参照表

| 示例     | 其他写法                      | 说明                                     |
| -------- | ----------------------------- | ---------------------------------------- |
| `x`      |                               | x 目录                                   |
| `x:0`    | `x:00`                        | x 目录 (空)                              |
| `x:1`    | `x:01`                        | x 目录下的一级文件                       |
| `x:10`   |                               | x 目录下的一级文件以及文件夹 (空)        |
| `x:11`   |                               | x 目录下的所有文件夹 (空)                |
| `x/*`    |                               | x 目录, 等同于 `x`                       |
| `x/*/`   |                               | x 目录下的一级文件夹                     |
| `x/*:0`  | `x/*/:0`, `x/*:00`, `x/*/:00` | x 目录下的一级文件夹 (空)                |
| `x/*:1`  | `x/*/:1`, `x/*:01`, `x/*/:01` |                                          |
| `x/*:10` | `x/*/:10`                     |                                          |
| `x/*:11` | `x/*/:11`                     | x 目录下的所有文件夹 (空), 等同于 `x:11` |

## 示例

> (引用自 `build/build_depsland/src_max.json`.)

```json
{
    "...": "...",
    "assets": [
        "CHANGELOG.zh.md",
        "apps/.bin:0",
        "build",
        "chore/pypi_blank",
        "config/depsland.yaml",
        "depsland",
        "dist:0",
        "dist/standalone:0",
        "oss/*:0",
        "pypi/*:0",
        "pypi/index/snapdep:0",
        "python:0",
        "temp:0",
        "test:0",
        "poetry.lock",
        "requirements.lock",
        "wiki/docs/.vitepress/dist"
    ]
}
```

产生的效果:

```
<dist>
|- CHANGELOG.zh.md
|= apps
   |= .bin  # empty folder
|= build
   |- ...
|= chore
   |= pypi_blank
      |- ...
|= config
   |- depsland.yaml
|= depsland
   |- ...
|= dist
   |= standalone  # empty folder
|= oss
   |= ...  # all empty folders
|= pypi
   |= ...  # all empty folders
   |= index
      |= snapdep  # empty folder
|= python  # empty folder
|= temp  # empty folder
|= test  # empty folder
|- poetry.lock
|- requirements.lock
|= wiki
   |= docs
      |= .vitepress
         |= dist
            |- ...
```

## 关联代码

- `depsland/manifest/manifest.py : Manifest : _update_assets`

