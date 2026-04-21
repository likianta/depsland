[# 开发者说明文档]

[## 占用端口说明]

[$yaml
    2180: depsland app builder
    2181: depsland app manager
    2182: depsland app store
    2183: depsland setup wizard - frontend
    2184: depsland setup wizard - backend
    2185: depsland installer online - frontend
    2186: depsland installer online - backend transceiver
    2187: depsland installer online - default client server
    2188: localnet resources
]

[## 命令缩写备注]

[
    lkrun: 来自 [` pip install lk-utils], 位于 [_ <venv>/Scripts/lkrun.exe]
    pom: [` poetry run python -m]
    pox: [` poetry run python]
    strun: [` poetry run -- streamlit run --browser.gatherUsageStats false --runner.magicEnabled false --server.headless true --server.port]
]

[## 构建]

[#~ 构建 Depsland Standalone]

[$sh
    # 获取帮助
    pox build/build_depsland/main.py -h

    # 无参数运行, 会得到 "dist/standalone/depsland-<version>" 文件夹.
    # 耗时: 如果依赖没有变化, 大约耗时 5s; 否则耗时 10s 以内.
    pox build/build_depsland/main.py

    # 自定义将要生成的版本
    ...

    # 构建并压缩.
    # 在上述结果的基础上, 会多生成一个 "dist/standalone/depsland-<version>.zip" 文件.
    pox build/build_depsland/main.py -z
    pox build/build_depsland/main.py -v ... -z
]

上传到 OSS: [
    = 将压缩包复制到 resources 文件夹下 
        [$sh cp dist/standalone/depsland-<version>.zip resources]
    = 手动上传到 OSS
        路径: [<aliyun_oss>/likianta-public-share/depsland-resources/depsland-<version>.zip]
]

[#~ 构建迷你启动器]

见 [sidework/mini_launcher/readme.zh.mo].
