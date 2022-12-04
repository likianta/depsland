from textwrap import dedent

from lambda_ex import grafting

from depsland import __version__ as depsland_version
from qmlease import QObject
from qmlease import slot


class Page3(QObject):
    _congrats_anim: QObject
    _has_played = False
    
    def __init__(self, main_page: QObject):
        super().__init__()
        
        # @grafting(main_page.current_page_changed.connect)
        # def _(index: int) -> None:
        #     if self._has_played:
        #         return
        #     if index == 2:  # the final page
        #         self._congrats_anim.start()
        #         self._has_played = True
    
    # @slot(object)
    # def init_view(self, congrats_anim: QObject) -> None:
    #     self._congrats_anim = congrats_anim
    
    @slot(result=str)
    def get_text(self) -> str:
        """ return markdown text. """
        return dedent('''
            # Congratulations!
            
            You have successfully installed depsland {version}.
            
            To get started, you can double-click the "Depsland" launcher on
            your desktop.
            
            Get touch with me on [GitHub][1] or start an instant chat with me
            in QQ/TIM (scanning QR code below).
            
            [1]: https://github.com/likianta/depsland
        ''').format(
            version=depsland_version,
        )
