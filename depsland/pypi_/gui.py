from gui_builder import GuiBuilder
from ..paths import pypi_model


class Application:
    
    def __init__(self):
        a, b, c = pypi_model.load_indexed_data()
        self.name_versions = a
        self.dependencies = b
        self.updates = c
        
        class Options:
            pass
        
        self.opt = Options
    
    # noinspection PyMethodMayBeStatic
    def _init_layout(self):
        builder = GuiBuilder()
        
        builder.add_col(
            builder.add_row(
                # builder.add_listbox()
            )
        )


def main():
    builder = GuiBuilder()
    
    builder.add_col(
        builder.add_row(
        
        )
    )
