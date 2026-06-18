# 为什么不使用 UV 工具链来处理 uv.lock

Astral uv 工具不满足以下需求:

- 我想要在 GUI 上显示下载依赖包的进度条, 但是 uv 的进度输出是专为现代终端 (TTY) 设计的, 且未提供 callback hook
- uv 没有暴露 Python API, 也就是说我们不能这样使用它: `import uv; uv.sync('uv.lock', cwd='.', progress=my_progress_with_gui)`
- uv 是并发的, 但目前我们的设计以单线程为主 (未来会支持多线程处理依赖)

相关阅读:

- https://chatgpt.com/share/6a323abf-17b4-83ee-bdb4-f6701a348206

