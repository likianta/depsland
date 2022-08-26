import lk_logger
lk_logger.setup(quiet=True, show_varnames=True)

print(':t0')

import flet
from flet import colors
from lambda_ex import hold

print(':t', 'import finished')


def main(page: flet.Page):
    print(':t', 'enter main function')
    
    with hold(page) as page:  # type: flet.Page
        
        with hold(flet.Container()) as body:  # type: flet.Container
            body.bgcolor = colors.AMBER_300
            body.expand = True
            
            with hold(flet.Row()) as row:  # type: flet.Row
                row.expand = True
        
        page.add(body)
    
    print(':t', 'construct page finished')
    return page


flet.app(target=main)
