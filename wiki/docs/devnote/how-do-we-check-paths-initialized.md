# 我们是怎么验证 Depsland 是首次运行的

## 起因

用户从各种渠道下载得到的 Depsland 安装包目前是一个 7z 或者 zip 格式的压缩包.

受限于 Widnows 的网络安全策略, 从网上下载的压缩包在解压后, 其中的 DLL 文件属性会处于 "锁定" 状态, 这就导致 Depsland 在启动时, 无法正常创建 GUI 窗口 (问题关联: toga, pythonnet).

我们已经找到了解锁的方法, 对于被锁定的 DLL, 只需解锁一次即可. 因此我们只想在 **首次** 启动 Depsland 时, 检查并解锁这些文件.

本文要讨论的就是, 我们是怎么判断 Depsland 是否为首次启动的.

## 遇到的问题

一个简单的想法是, 通过读取一个配置文件, 里面用一个 `initialized: bool` 字段来判断即可.

首次启动时, 读到值是 false, 完成解锁后, 把它设为 true 再写入文件, 这看起来很简单.

但实际情况是复杂的, 比如我们遇到了这种使用场景:

> 用户 A 解压了压缩包, 完成了首次运行, 又把解压后的文件夹重新打包, 通过网盘分享给了用户 B.
>
> 用户 B 在解压后, 文件此时重新处于 "锁定" 状态, 而他的配置文件又不小心处于 `initialized=true` 状态, 于是导致了 Depsland 在用户 B 那里启动失败.

因此, 我们不能简单地用 `initialized: bool` 来判断是否首次运行.

## 解决方法

针对上面的问题, 我们调整了 `initialized` 的值的格式: `initialized: <apppath>-<created_time>-<bool>`.

新格式的作用方法:

- 假设用户 A 的 `apppath` 是 "C:/Users/A/Programs/Depsland", 用户 B 的是 "D:/Downloads/Depsland", 那么 Depsland 可以认定发生了变化, 系首次启动.
- 假设用户 A 的 `created_time` 是时间 T0, 在经过再压缩 - 再解压后, 文件的创建时间会发生变化, 所以 B 的 `created_time` 是时间 T1, 二者差异可判断为系首次启动.