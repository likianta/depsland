import PySimpleGUI as Gui
from functools import partial


class Window:
    
    def __init__(self, title):
        self._start = partial(Gui.Window, title)
        
    def start(self, layout):
        self._start(layout)
