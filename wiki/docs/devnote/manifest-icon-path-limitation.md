## 为什么 Manifest 中的图标路径必须在项目目录内?

示例:

```json5
// DON'T
{
    // ...
    "launcher": {
        // ...
        "icon": "<other_directory_than_current_project>/<...>/image.ico"
    }
}

// DO
{
    // ...
    "launcher": {
        // ...
        "icon": "<current_project>/<...>/image.ico"
    }
}
```

为什么: 

传统的创建启动器的方式比较花时间, Depsland 则采用了一种特别的方式快速创建, 这需要用到本地的 ico 文件.

如果 `icon` 指向的路径不在项目内, 那么 icon 就无法上传到云端, 则客户端无法从云上拉取该文件, 客户端没有了 icon, 也就无法通过上述方式 **快速** 创建启动器.

所以我们要求如果提供了 `icon`, 那么该文件必须位于项目目录内.

