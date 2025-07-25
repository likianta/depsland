# 迷你启动器

## 为什么要有迷你启动器?

Depsland 的自身安装包体积在 70MB 以上, 如果考虑到以 "shipboard" 模式封装的第三方应用, 其体积可能高达百兆, 这对于多数人来说是一个可感知的体积, 无论是下载, 分发, 解压和拷贝, 对于硬件资源较差的电脑都是不友好的.

为了减轻由于初始的体积给人造成的不好的印象, 我们制作了迷你启动器.

迷你启动器的体积在 5MB 左右, 它在启动时会优先检测并复用本地已有的资源, 仅下载缺少的组件 (注意这需要联网), 从而减轻网络下载压力, 这对于想要初次使用/想要尝鲜的新用户来说, 能一定程度减少焦虑感.

## 工作原理

```mermaid
graph TB;

A[开发者创建迷你启动器];
B["通过 微信/网盘/局域网/优盘 等方式发给用户"];
C[用户下载并运行];
D[检查用户运行环境];
E["Depsland 已安装?"];
F["Depsland 版本满足要求?"];
G[目标应用已安装?];
H[目标应用版本满足要求?];
I[启动应用];
J[升级应用];
K[下载应用];
L["升级 Depsland"];
M["下载 Depsland"];

subgraph **分发**;
A --> B;
B --> C;
end

subgraph **启动器**;
C --> D;
D --> E;
E -- 是 --> F;
E -- 否 --> M;
F -- 是 --> G;
F -- 否 --> L;
G -- 是 --> H;
G -- 否 --> K;
H -- 是 --> I;
H -- 否 --> J;
J --> I;
K --> I;
L --> G;
M --> K;
end
```

## 如何创建迷你启动器

见 `/sidework/mini_launcher/by_nuitka/factory.py`.

```sh
python sidework/mini_launcher/by_nuitka/factory.py -h
python sidework/mini_launcher/by_nuitka/factory.py main -h
python sidework/mini_launcher/by_nuitka/factory.py manifest -h
...
```

