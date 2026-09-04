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

---

### 2026-09-04

我最近补全了补丁相关的功能. 现在需要你帮忙制作一个流程图, 以便于我向其他人介绍补丁工作流程. 具体如下:

```
用户: 用户启动应用
应用: 创建一个子线程, 启动检查更新器
应用: 更新器查询服务器是否有更新
    是: 
        服务器: 检测到有新的用户连接
        服务器: 对比用户的补丁版本和线上补丁版本差异
        服务器: 将差异结果导出为资产变化表
        服务器: 将变化表以及 "新增/更新" 的资产进行打包推送
        用户: 收到变化表和更新资产, 储存在本地补丁缓存
    否:
        用户: 结束子线程
用户: 启动 "Check Updates.exe", 它会激活本地补丁工具
补丁工具: 本地补丁应用器检查本地缓存的最新补丁
补丁工具: 根据资产变化表, 完成 "先删后增" 操作
补丁工具: 完成后退出
用户: 重新启动应用, 会看到升级后的内容
```

以上流程, 使用 HTML 或者 SVG 制作, 将源代码保存到 `./wiki/src/devnote/patch-maker-workflow.html (or .svg)`. 之后我会打开浏览器自己看一下效果.

补充说明: 流程中使用中文描述.
