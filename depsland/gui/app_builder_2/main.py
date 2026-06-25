if __name__ == '__main__':
    __package__ = 'depsland.gui.app_builder_2'

import os

import streamlit as st
import streamlit_canary as sc

from ...api import build_project


def main():
    st.title('Depsland App Builder Lite')
    builder_profile = sc.tree_select_with_input(
        'Input builder profile (.json)', show_recent=True
    )
    if builder_profile:
        print(builder_profile, ':n')

    kwargs = {}

    x = st.text_input(
        'New version',
        '$auto_increment',
        width=200,
        help=(
            """
            You can input a version like "0.1.0" or "0.1.0a0" for alpha, 
            "0.1.0b0" for beta release.

            There are two special values:

            - `$auto_increment`: auto increment the version.
            - `$remain`: remain version unchanged.

            Leave empty also means auto increment.
            """
        ),
    )
    if x == '' or x == '$auto_increment':
        kwargs['new_version'] = ''
    elif x == '$remain':
        kwargs['remain_last_version'] = True
    else:
        kwargs['new_version'] = x

    kwargs['minify_deps'] = 1 if st.checkbox('Minify dependencies') else 0

    with sc.row():
        kwargs['encrypt_packages'] = 1 if st.checkbox('Encrypt packages') else 0
        if st.toggle('Reuse last encrypted packages'):
            kwargs['encrypt_packages'] = 2

    kwargs['publish'] = st.radio(
        'Publish mode',
        (0, 1, 2),
        format_func=lambda x: (
            'No publish'
            if x == 0
            else 'Generate local distribution'
            if x == 1
            else 'Publish to Depsland Store'  # 2
        ),
        index=1,
        # horizontal=True,
    )
    if kwargs['publish'] == 2:
        if not os.getenv('DEPSLAND_CONFIG_ROOT'):
            st.warning(
                'Depsland requires OSS credentials to publish to '
                'Depsland Store.'
            )
    kwargs['compress_result'] = st.checkbox(
        'Compress result', disabled=kwargs['publish'] != 1
    )

    if st.button(
        'Start building', type='primary', disabled=not builder_profile
    ):
        print(':lv2', kwargs)
        assert builder_profile
        build_project(builder_profile, **kwargs)


if __name__ == '__main__':
    main()
