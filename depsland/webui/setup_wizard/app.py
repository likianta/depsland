if __name__ == '__main__':
    __package__ = 'depsland.webui.setup_wizard'

import typing as t

import streamlit as st
import streamlit_canary as sc
from argsense import cli
from streamlit_extras.bottom_container import bottom as st_bottom_bar

from ..progress_bar import progress_bar
from ...api import install_by_appid

if not (_state := sc.session.get_data()):
    _state.update({'finished': False})


@cli
def main(
    app_name: str,
    appid: str,
    description: str = None,
    dry_run: bool = False
) -> None:
    # print(app_name, appid, dry_run, sys.argv, sys.orig_argv, ':lv')
    
    if not _state['finished']:
        st.title(f'Installing :blue[{app_name}]...')
    else:
        st.title(app_name)
    
    with st.sidebar:
        st.image('chore/setup_wizard_logo.png')
        # st.subheader(app_name)
        st.markdown(
            '<h2 style="text-align: center; color: black;">{}</h2>'
            .format(app_name),
            unsafe_allow_html=True,
        )
        if description:
            st.divider()
            st.markdown(description)
    
    if dry_run:
        _play_demo()
    else:
        if not _state['finished']:
            with progress_bar() as placeholder:
                install_by_appid(appid)
            _state['finished'] = True
            with placeholder:
                st.success(
                    'Installation done.\n\n'
                    'You can now close this window and restart the same app '
                    'again, there will launch target app instead of wizard.'
                )
        else:
            # st.success('Installation done.')
            st.success(
                'Installation done.\n\n'
                'You can now close this window and restart the same app again, '
                'there will launch target app instead of wizard.'
            )
    
    with st_bottom_bar():
        # TODO
        # cols = iter(st.columns(2))
        # with next(cols):
        #     if sc.long_button('Finish'):
        #         sc.kill()
        # with next(cols):
        #     if sc.long_button('Finish and run', type='primary'):
        #         proc = run_cmd_args(
        #             sys.executable, '-m', 'depsland', 'run', appid,
        #             verbose=True, blocking=False, force_term_color=True,
        #         )
        #         atexit.unregister(proc.kill)
        #         sc.kill(except_pids=(proc.pid,))

        if sc.long_button(
            'Finish', type='primary', help='Click to close this window.'
        ):
            sc.kill()


def _play_demo() -> None:
    from lk_utils import wait
    
    def fake_progress() -> t.Iterator[float]:
        for p in wait(3, 50e-3, False):
            yield p.percent
    
    part1 = st.empty()
    with part1:
        st.write('Downloading packages from the internet...')
    prog1 = st.progress(0)
    
    part2 = st.empty()
    with part2:
        st.write('Unpacking packages...')
    prog2 = st.progress(0)
    
    for p in fake_progress():
        prog1.progress(p, '{:.2%}'.format(p))
    with part1:
        st.write('Downloading packages from the internet... :green[done]')
    
    for p in fake_progress():
        prog2.progress(p, '{:.2%}'.format(p))
    with part2:
        st.write('Unpacking packages... :green[done]')


if __name__ == '__main__':
    # strun 2181 depsland/webui/setup_wizard/app.py
    #   -- 'Hello World' hello_world 'Demo play installing hello-world app.'
    #   --dry-run
    # pox -m pyapp_window --port 2181 --size 1340x960
    #   --title 'Depsland Setup Wizard'
    st.set_page_config('Depsland Setup Wizard')
    # main('Hello World', 'hello_world')
    cli.run(main)
