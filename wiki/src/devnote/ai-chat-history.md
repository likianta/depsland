### 2026-07-06

请聚焦在 `./depsland/gui/app_builder` 这个目录, 不考虑其他路径下的模块. 我想让你把 `./depsland/gui/app_builder/i18n.py` 拆分到 `./depsland/gui/app_builder/languages/*.yaml`, 并且在 `i18n.py` 中, 用下面的方法加载文件:

```python
from lk_utils import fs

def self_check():
    ch = fs.load(fs.here('languages/chinese.yaml'))
    en = fs.load(fs.here('languages/english.yaml'))
    for key in ch:
        if key not in en:
            print('missing key in english.yaml', key)
    ...

i18n = fs.load(fs.here('languages/chinese.yaml'))  # developing...
```

### 2026-07-15

我想制作一个补丁工具, 用来给客户电脑上已经安装的旧版本应用打补丁, 这样用户不需要下载新的完整版应用, 就能获得大部分功能更新与修复.

请先阅读 `./wiki/src/devnote/how-to-patch.md`, 了解技术背景 (文中提到了 V 语言, 请忽略它, 我们接下来要用的是 Go 语言.)

然后, 聚焦于 `./sidework/patch_maker/` 这个目录, 你需要先阅读该目录下的所有脚本, 理解我当前的工作进度.

最后, 我需要你基于 `./sidework/patch_maker/patch_extractor_prototype.py`, 将它用 Go 语言实现, 得到 `patch_extractor.go` 文件.

目前仅进行代码编写工作, 不用考虑 Go 编译等问题.

