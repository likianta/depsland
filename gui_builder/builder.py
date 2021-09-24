import PySimpleGUI as Gui


# noinspection PyMethodMayBeStatic
class GuiBuilder:
    
    def add_row(self, *elements):
        return list(elements)
    
    def add_col(self, *rows):
        return list(rows)

    def add_listbox(self, values):
        return Gui.Listbox(values)
