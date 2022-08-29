from lk_utils import relpath

from hot_reloader import run

run(relpath('view.py'),
    app_name='Depsland',
    window_width=600, window_height=400)
