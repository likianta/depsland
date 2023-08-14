# 什么是 Package ID

package id 是由 `包名 + 版本号` 组成的名称, 它具有以下特性:

- package id 是唯一的
- package id 关联一个或多个路径 (通常是两个及以上)

    例如:

    ```
    lk_logger-5.6.2
    |= lk_logger
    |= lk_logger-5.6.2.dist-info

    lkfmt-0.3.0a17
    |= lkfmt
    |= lkfmt-0.3.0a17.dist-info
    |- bin/lkfmt

    pyyaml-6.0.1
    |= yaml
    |= PyYAML-6.0.1.dist-info

    six-1.16.0
    |- six.py
    |= six-1.16.0.dist-info
    ```

## Package ID 特征

- 包名必须是全小写字母, 数字和下划线
- 版本号必须符合语义版本规范
- 包名与版本之间使用连字符连接

## Package ID 用途

我们使用 package id 来标识一个包, 在服务器端执行增量更新时判断一个包是否已经上传, 以及在客户端执行增量更新时判断是否需要下载.

此外, package id 也是 depsland 用于管理虚拟环境的方式.

关联代码:

- `depsland.venv.target_venv.TargetVenvIndex.deps_map`
- `depsland.manifest.manifest`
- `depsland.manifest.manifest._update_dependencies`
- `depsland.api.dev_api.publish`
