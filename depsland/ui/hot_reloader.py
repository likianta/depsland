import flet
import lk_logger
from lambda_ex import later, hold

__all__ = ['run']

lk_logger.setup(quiet=True, show_varnames=True)


def run(target_file: str, show_fab=False, **kwargs):
    from functools import partial
    from lk_utils.filesniff import normpath
    target_file = normpath(target_file, force_abspath=True)
    # print(target_file)
    print(':t0s')
    flet.app(
        kwargs.get('app_name', 'Hot Reloader'),
        target=partial(
            _indexing,
            target_file=target_file,
            show_fab=show_fab,
            **kwargs
        )
    )


def _indexing(page: flet.Page, target_file: str, **kwargs):
    print(':t', 'start indexing reloader page')
    
    app_name = kwargs.get('app_name', 'Hot Reloader')
    win_bg = kwargs.get('win_bg', '#f5f7fd')
    win_width = kwargs.get('window_width', 800)
    win_height = kwargs.get('window_height', 600)
    show_fab = kwargs.get('show_fab', False)
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
        
        page.controls.append(placeholder)
        
        if show_fab:
            global _fab
            with hold(_fab := flet.FloatingActionButton()):
                from flet import icons
                _fab.icon = icons.REFRESH
                _fab.width = 28
                _fab.height = 28
                _fab.on_click = lambda _: _reload(page, target_file)
            page.controls.append(_fab)
        
        page.update()
    
    print(':t', 'reloader construction complete')


_fab: flet.FloatingActionButton | None = None


def _reload(root: flet.Page, target_file: str):
    from lk_logger.console import con_error
    root.controls.clear()
    try:
        exec(open(target_file).read(), {
            'root'    : root,
            'print'   : print,  # this points to `lk_logger.lk.log` method.
            '__file__': target_file,
        })
    except Exception:
        con_error()
    else:
        if _fab is not None:
            root.controls.append(_fab)
        root.update()


if __name__ == '__main__':
    run('view.py')
