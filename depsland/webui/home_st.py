import streamlit as st
import streamlit.components.v1 as comp

from depsland import paths

st.set_page_config(
    page_title='Depsland',
    page_icon=paths.build.launcher_ico,
)


def main():
    st.title('Welcome to Depsland')
    st.markdown('''
        [Depsland](https://github.com/likianta/depsland) is a fundamental
        infrastructure to install, update and manage your Python applications.
    ''')
    
    with st.container():
        st.write('localy installed apps:')
        
        comp.html('''
            <link
                rel="stylesheet"
                href="depsland/webui/bulma.min.css">
            <link
                rel="stylesheet"
                href="bulma.min.css">
            <link
                rel="stylesheet"
                href="https://cdn.jsdelivr.net/npm/bulma@0.9.4/css/bulma.min.css">
            <section class="section">
                <div class="container">
                    <h1 class="title">
                        hello world
                    </h1>
                    <p class="subtitle">
                        this is bulma css
                    </p>
                    <div class="container">
                        <button class="button">btn1</button>
                        <button class="button">btn2</button>
                        <button class="button">btn3</button>
                    </div>
                </div>
            </section>
        ''')
        
        # fake_app_names = ('app1', 'app2', 'app3', 'app4', 'app5', 'app6')
        # for i, name in enumerate(fake_app_names):
        #     with st.container():
        #         col0, col1 = st.columns(2)
        #         with col0:
        #             st.write(f'{i + 1}. {name}')
        #         with col1:
        #             st.button('launch', key=f'launch_{name}')
        #         st.markdown('---')


if __name__ == '__main__':
    main()
