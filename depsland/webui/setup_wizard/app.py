# import streamlit as st

if __name__ == '__main__':
    __package__ = 'depsland.webui.setup_wizard'
    # st.set_page_config('Depsland Setup Wizard')

import streamlit as st


def main(appid: str) -> None:
    st.title(appid.replace('_', ' ').title())
    
    with st.sidebar:
        st.image(
            r'C:\Likianta\pictures\收集\2024\83244543.png',
            # r'C:\Likianta\temp\2024-12\jlsemi-logo\omnicomm-logo-splash.png',
            # use_container_width='always',
        )
    
    part1 = st.empty()
    with part1:
        st.write('Downloading packages from the internet...')
    prog1 = st.progress(0)
    
    part2 = st.empty()
    with part2:
        st.write('Unpacking packages...')
    prog2 = st.progress(0)
    
    for p in _fake_progress():
        prog1.progress(p, '{:.2%}'.format(p))
    with part1:
        st.write('Downloading packages from the internet... :green[done]')
    
    for p in _fake_progress():
        prog2.progress(p, '{:.2%}'.format(p))
    with part2:
        st.write('Unpacking packages... :green[done]')


def _fake_progress():
    from lk_utils import wait
    for p in wait(3, 50e-3, False):
        yield p.percent


if __name__ == '__main__':
    # strun 2181 depsland/webui/setup_wizard/app.py
    # pox -m pyapp_window --port 2181 --size 1420x910
    #   --title 'Depsland Setup Wizard'
    st.set_page_config('Depsland Setup Wizard')
    main('hello_world')
