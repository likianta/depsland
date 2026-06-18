# Depsland 在线安装向导

## 启动

### 在测试模式运行

```sh
pox run/setup_wizard.py debug
```

它会在本地启动一个服务器, 模拟云服务器.

它会在本地启动一个客户端, 模拟用户在他的电脑上双击 "Hello World.exe" (某个迷你启动器) 时的情况.

最后, 它会在 localhost:3001 端口启动在线安装向导的 GUI, 你需要手动打开浏览器, 访问 http://localhost:3001, 你将看到下图的界面:

...

这也是用户在他的电脑上将看到的界面.

### 在生产模式下启动

```sh
pom run start_depsland_online_service $bore_frp_secret
```

