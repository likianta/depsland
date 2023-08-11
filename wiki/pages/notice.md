# 注意事项

## 虚拟环境

使用 depsland 之前, 准备一个项目的虚拟环境是 **必须** 的.

depsland 支持以下虚拟环境形式:

1. poetry (推荐)
2. venv (通过 virtualenv 或者 pycharm 等方式创建)

如果你的项目没有用到虚拟环境, 用的是全局的 site-packages, depsland 提供了一个实验性的解决方案:

1. 请确保你的项目下有一个 requirements.txt 文件
2. 运行以下命令

    ```sh
    # get help
    depsland make-requirements-lock -h
    # generate "requirements.lock"
    depsland make-requirements-lock ./requirements.txt
    ```

