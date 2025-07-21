# 关于 Rust 启动器的构想

## 要解决的问题

Depsland 的体积问题导致了多个方面的不良影响.

用户从下载 - 解压 - 运行 - 升级都体验不佳.

我们在构想一个基于 Rust 语言编写的启动器, 来这样解决问题:

- 下载: rust launcher 将采用极为迷你的体积, 无论是聊天, 邮件, 网盘等任何传输形式都可以分发.
- 解压: rust launcher 双击启动, 无需解压.
- 运行: *这个问题没有解决.*
- 升级: rust launcher 将会调用 depsland 的增量更新形式. 与之前的区别是, 之前用户需要手动完成这一步, 尽管难度不高, 但告诉用户怎么做 (特别是出现报错时该怎么做) 仍然是困难的事, rust launcher 则全程自动化完成, 它可以做到 "无感升级".

## 工作流程概述

```mermaid
graph TB;
  subgraph 用户;
    A[用户获得 Rust 启动器]-->B[运行启动器];
    end
  subgraph Rust 启动器;
    B--启动器工作-->C[检查环境变量];
    C-->D[环境变量中是否存在 'DEPSLAND'?];
    D--是-->E["运行命令 'depsland runx {appid}'"];
    D--否-->F["下载 Depsland (约 40MB)"];
    F-->E;
    end
  subgraph Depsland;
    E--Depsland 工作-->G[目标程序是否已下载?];
    G--是-->H[目标已更新到目标版本?];
    G--否-->I[下载目标程序];
    I-->H;
    H--是-->J[运行目标程序];
    H--否-->K[更新程序到指定版本];
    K-->J;
    end
```

