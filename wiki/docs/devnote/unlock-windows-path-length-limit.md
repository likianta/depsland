# 解锁 Windows 路径长度限制

windows 默认的路径长度限制是 260 字符, 在某些情况下会导致应用升级失败.

最近遇到过的案例是, 我们对某个应用使用了 uuid 作为 appid, 这是一个比较长的字符串. 当用户把这个应用解压到一个层级较深的自定义目录后, 用户点击 "Check Updates.exe" 去升级, 会在 `depsland.utils.ziptool.extract_file` 中发生报错.

报错信息是: `FileNotFoundError: ...`, 但实际上是由于某些解压路径超过了 260 字符导致的.

为了解决这个问题, 我们从两方面入手:

1. 不使用长的 uuid 作为 appid, 我们使用较短的随机码 (比如 8 位数)
2. `depsland.utils.ziptool.extract_file` 在 windows 下会给路径加上前缀 `"\\\\?\\"`. 该方法可以有效解决路径长度问题, 目前我们只在这一个地方使用了这个方案, 其他地方 (比如 `os.listdir`, `os.move`) 是否也要这样做, 仍待考虑.
