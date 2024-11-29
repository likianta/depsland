# 观察 argsense cli 在继承调用时的 sys.argv 传递行为及影响

初步认为, argsense 0.4.3- 版本不支持继承调用, 我将在 0.5.0 版本中使用一种 "即时消除参数" 的策略来解决这个问题.

## 测试过程

1. 打开命令行
2. `depsland install hello_world_cli`
3. `hello_world_cli --help`: 看是否正常输出帮助信息
3. `hello_world_cli run --name Alice`: 看是否正常输出 `Hello, Alice!`
