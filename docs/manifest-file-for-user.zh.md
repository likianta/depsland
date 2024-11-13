# 面向用户的清单文件格式说明

## 文件名和后缀

清单文件的文件名没有要求, 你可以起任意名称. 默认情况下, 使用 `depsland init` 会在项目下生成 "manifest.json" 的默认文件名.

此外, 清单文件对于路径也没有要求, 你可以将它放在任意路径下, 但有一些注意事项需要关注, 我们在后续说明. 默认情况下, 使用 `depsland init` 会在项目的根目录下创建该文件.

清单文件支持以下后缀格式: ".json", ".yaml", ".yml", ".pkl".

其中前三者是用户可编辑的格式, 最后一种是程序缓存的格式. 本文对 json 格式进行讲解, yaml 可参考 json 来理解.

## 文件格式 (以 JSON 为例)



```json5
{
    // 应用 id.
    "appid": "hello_world",
    // ...
    "launcher": {
        "command": "<python> run.py --name 'Likianta D'",
        //  或者: "command": ["<python>", "run.py", "--name", "Likianta D"]
        "icon": "",
        "show_console": true,
        "enable_cli": false,
        "add_to_desktop": false,
        "add_to_start_menu": false,
    }
}
```

## 其他说明

### "manifest.pkl" 与 "manifest.json/yaml" 具体有什么区别?

...