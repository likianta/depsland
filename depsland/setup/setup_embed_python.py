from embed_python_manager import EmbedPythonManager


def setup_embed_python(pyversion: str, dst_dir, **kwargs):
    manager = EmbedPythonManager(pyversion)
    manager.change_source('npm_taobao_org.yml')
    manager.deploy(
        kwargs.get('add_pip_suits', True),
        kwargs.get('add_pip_scripts', True),
        kwargs.get('add_tk_suits', True),
    )
    manager.move_to(dst_dir)
    # return manager.model
