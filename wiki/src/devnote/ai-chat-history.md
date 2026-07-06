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



