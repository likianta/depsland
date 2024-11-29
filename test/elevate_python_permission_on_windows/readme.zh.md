## 生成 exe 文件

```shell
py build/build.py bat-2-exe unittests\elevate_python_permission_on_windows\run.bat
py build/build.py bat-2-exe unittests\elevate_python_permission_on_windows\sudo_run.bat
py build/build.py bat-2-exe unittests\elevate_python_permission_on_windows\sudo_run_no_window.bat -C
```

## 现象

1. 双击 run.exe, 你的电脑可能会出现权限不足的警告
2. 双击 sudo_run.exe, 你的电脑先出现一个黑窗口, 快速消失, 然后出现第二个窗口, 提示你权限充足
3. 双击 sudo_run_no_window.exe, 你的电脑会闪现一个窗口并快速消失 (比 2 更快), 然后出现第二个窗口, 提示你权限充足

我们在尝试解决 sudo_run_no_window.exe 的第一个窗口闪现的问题, 初步认为它是一个 bug. 预期的现象应该是第一个窗口从未出现.

相关工作见 `~/depsland/utils/gen_exe/main.py`.
