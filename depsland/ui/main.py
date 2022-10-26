from lk_utils import xpath

from hot_reloader import run

run(xpath('view.py'),
    app_name='Depsland',
    show_fab=True,
    window_width=600, window_height=400)
