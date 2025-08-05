"""
TODO: we may use `gettext` in the future.
"""
from lk_utils import dedent


def _text_block(text: str) -> str:
    # return dedent(text, join_sep='\\')
    return dedent(text, join_sep='\\').replace('\n', '  \n')
    # return dedent(text, join_sep='\\').replace('\n', '\n\n')


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
        目前, 标识码的格式被设计为一种可读的风格; 未来可能考虑使用 UUID 生成以确保全局唯一性.
        '''
    )
    appid_regenerate = '重新生成'
    appinfo = '应用信息'
    appname = '应用名称'
    ask_project_path = '请输入项目路径'
    assets_title = '资产清单 (文件树)'
    title = 'Depsland 应用构建器'
    title_online = 'Depsland 应用构建器 (在线版)'
    version = '版本'
    version_alpha = 'Alpha'
    version_beta = 'Beta'
    version_bump = '提升版号'
    version_formal = '正式版'
    version_switch = '切换'


i18n = Chinese()
