import streamlit as st


def main() -> None:
    with st.expander('System', True):
        add_to_path = st.checkbox(
            'Add to environment PATH',
            help=(
                'Add depsland executable path to environment PATH. \n\n'
                'This allows you to run `depsland` from the command line.'
            )
        )
        # st.caption(
        #     'Add depsland executable path to environment PATH. \n\n'
        #     'This allows you to run `depsland` from the command line.'
        # )
        add_to_desktop = st.checkbox('Create desktop shortcut')
    
    if st.button('Apply settings', type='primary'):
        print(add_to_path, add_to_desktop)
        st.success('Settings applied.')
