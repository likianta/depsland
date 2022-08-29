import flet
import lk_logger
from lambda_ex import later

__all__ = ['run']

lk_logger.setup(quiet=True, show_varnames=True)


def run(target_file: str, **kwargs):
    from functools import partial
    from lk_utils.filesniff import normpath
    target_file = normpath(target_file, force_abspath=True)
    # print(target_file)
    print(':t0')
    flet.app(
        kwargs.get('app_name', 'Hot Reloader'),
        target=partial(_indexing, target_file=target_file, **kwargs)
    )


def _indexing(page: flet.Page, target_file: str, **kwargs):
    from lambda_ex import hold
    
    print(':t', 'start indexing reloader page')
    
    app_name = kwargs.get('app_name', 'Hot Reloader')
    win_bg = kwargs.get('win_bg', '#f5f7fd')
    win_width = kwargs.get('window_width', 800)
    win_height = kwargs.get('window_height', 600)
    del kwargs
    
    with hold(page):
        page.title = app_name
        page.window_width = win_width
        page.window_height = win_height
        page.window_center()
        page.padding = 0
        page.bgcolor = win_bg
        page.on_keyboard_event = slot = later()
        
        @slot.bind
        def on_key(e: flet.KeyboardEvent):
            # `ctrl + r` to reload view.
            # print(e.key, e.shift, e.ctrl)
            if e.ctrl and e.key == 'R':
                _reload(page, target_file)
        
        with hold(placeholder := flet.Container()):
            placeholder.alignment = flet.alignment.center
            placeholder.bgcolor = win_bg
            placeholder.expand = True
            
            with hold(text := flet.Text()):
                text.value = 'Press `CTRL + R` to reload.'
                text.color = '#666666'
                text.text_align = 'center'
            
            placeholder.content = text
        
        page.add(placeholder)
    
    print(':t', 'reloader construction complete')


def _reload(root: flet.Page, target_file: str):
    root.controls.clear()
    exec(open(target_file).read(), {
        'root'    : root,
        'print'   : print,  # this points to `lk_logger.lk.log` method.
        '__file__': target_file,
    })
    root.update()


if __name__ == '__main__':
    run('view.py')
