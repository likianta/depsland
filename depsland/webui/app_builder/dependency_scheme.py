import streamlit as st
import streamlit_canary as sc
from lk_utils import fs
from .i18n import i18n


def main(root: str):
    way = st.radio(
        i18n.deps_scheme_ask,
        (
            i18n.deps_scheme_0,
            i18n.deps_scheme_1,
            i18n.deps_scheme_2,
            i18n.deps_scheme_3,
        ),
        index=3,
    )
    match way:
        case i18n.deps_scheme_0:
            return
        case i18n.deps_scheme_1:
            assert fs.exist(root + '/poetry.lock')
        case i18n.deps_scheme_2:
            pass
        case i18n.deps_scheme_3:
            dir_i = sc.path_input(
                i18n.deps_venv_ask, parent=root, help=i18n.deps_venv_help
            )
            dir_o = sc.path_input(
                i18n.deps_output_ask, parent=root
            )
