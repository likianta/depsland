import flet

from faker import Faker
from lambda_ex import hold, xlambda
from base.swipe_view import SwipeView

fake = Faker()


# noinspection PyPep8Naming
class color:
    panel_bg = '#15141a'
    win_bg = '#050408'


def main(page: flet.Page):
    print(':t0')
    
    with hold(page):
        page.padding = 0
        # page.window_width = 600
        # page.window_height = 400
        
        with hold(root := flet.Container()):
            root.bgcolor = color.win_bg
            root.expand = True
            root.border_radius = 0
            root.margin = 0
            
            with hold(row := flet.Row()):
                with hold(sidebar := flet.Column()):
                    sidebar.expand = 25
                    
                    sidebar.controls.extend((
                        b1 := flet.TextButton('one'),
                        b2 := flet.TextButton('two'),
                        b3 := flet.TextButton('three'),
                    ))
                
                with hold(main_view := flet.Container()):
                    main_view.bgcolor = color.panel_bg
                    main_view.expand = 75
                    
                    with hold(swipe := SwipeView()):
                        swipe.width = 400
                        swipe.height = 400
                        # swipe.expand = True
                        print(swipe.width, swipe.height)
                        
                        swipe.controls.extend((
                            flet.Container(bgcolor='#ff0000', expand=True),
                            flet.Container(bgcolor='#00ff00', expand=True),
                            flet.Container(bgcolor='#0000ff', expand=True),
                        ))
                    
                        b1.on_click = xlambda('e', """
                            print('switch to page 0')
                            swipe.switch_to(0)
                        """)
                        b2.on_click = xlambda('e', """
                            print('switch to page 1')
                            swipe.switch_to(1)
                        """)
                        b3.on_click = xlambda('e', """
                            print('switch to page 2')
                            swipe.switch_to(2)
                        """)
                    
                    main_view.content = swipe
                    
                row.controls.extend((sidebar, main_view))
            
            root.content = row
        
        page.add(root)
    
    print(':t', 'complete')


main(root)  # noqa
