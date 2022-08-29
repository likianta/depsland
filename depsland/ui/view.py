import flet
from lambda_ex import hold


# noinspection PyPep8Naming
class color:
    panel_bg = '#15141a'
    win_bg = '#050408'


def main(page: flet.Page):
    with hold(page):
        page.padding = 0
        page.window_width = 600
        page.window_height = 400
        
        with hold(root := flet.Container()):
            root.bgcolor = color.win_bg
            root.expand = True
            root.border_radius = 0
            root.margin = 0
            
            with hold(row := flet.Row()):
                with hold(sidebar := flet.Column()):
                    sidebar.expand = 25
                    
                    sidebar.controls.extend((
                        flet.TextButton('one'),
                        flet.TextButton('two'),
                        flet.TextButton('three'),
                    ))
                
                with hold(main_view := flet.Container()):
                    main_view.bgcolor = color.panel_bg
                    main_view.expand = 75
                
                row.controls.extend((sidebar, main_view))
            
            root.content = row
        
        print('complete')
        page.add(root)


main(root)  # noqa
