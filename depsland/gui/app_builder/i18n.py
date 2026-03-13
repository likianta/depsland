"""
TODO: we may use `gettext` in the future.
"""
from lk_utils import dedent


def _text_block(text: str) -> str:
    return (
        dedent(text, join_sep='\\')
        .replace('\n\n', '<br>')
        .replace('\n', '  \n')
        .replace('<br>', '\n\n')
    )


class English:
    appid = 'AppID'
    appid_regenerate = 'regenerate'
    appinfo = 'Application Infomation'
    appname = 'AppName'
    title = 'Depsland App Builder'
    title_online = 'Depsland App Builder Online'


class Chinese(English):
    appid = '应用标识码'
    appid_help = _text_block(
        '''
        应用标识码由 Depsland 程序生成, 具有唯一性. 该标识码被用作发布到商店时的识别依据.
        目前, 标识码的格式被设计为一种可读的风格; 未来可能考虑使用 UUID \\
        生成以确保全局唯一性.
        '''
    )
    appid_regenerate = '重新生成'
    appinfo = '应用信息'
    appname = '应用名称'
    ask_proj_path = '请输入项目路径'
    deps_output_ask = '压缩结果输出目录'
    deps_scheme_ask = '你想要如何集成 Python 依赖?'
    deps_scheme_0 = '不包含'
    deps_scheme_1 = '云托管'
    deps_scheme_2 = '直接嵌入 (不推荐)'
    deps_scheme_3 = '压缩后嵌入'
    deps_venv_ask = '请提供虚拟环境目录'
    deps_venv_help = _text_block(
        '''
        此目录为 "site-packages" 所在的目录, 格式可以是绝对路径, \\
        或相对于项目根目录的相对路径.

        示例: ".venv/Lib/site-packages", "./chore/my_packages", \\
        "C:/Users/YourName/.poetry/hello-world-py312/Lib/site-packages".
        '''
    )
    filetree_title_left = '文件树'
    filetree_title_right = '结果预览'
    proj_desc = _text_block(
        '''
        Depsland 应用构建器可将你的 Python 项目打包为独立应用, 并提供 "离线发布", \\
        "在线升级" 两种安装方式.
        '''
    )
    tab_title_1_assets = '资产清单'
    tab_title_2_deps_scheme = '依赖处理'
    tab_title_3_enc = '代码加密'
    title = 'Depsland 应用构建器'
    title_online = 'Depsland 应用构建器 (在线版)'
    version = '版本'
    version_alpha = 'Alpha'
    version_beta = 'Beta'
    version_bump = '提升版号'
    version_formal = '正式版'
    version_switch = '切换'


i18n = Chinese()
