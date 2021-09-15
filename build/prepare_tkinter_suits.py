from embed_python_manager import EmbedPythonManager
from embed_python_manager.tk_suits import copy_tkinter

manager = EmbedPythonManager('python38')

if not manager.has_tkinter:
    copy_tkinter(
        input('system python dir (python38): '),
        manager.model.tk_suits_py3
    )
