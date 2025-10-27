import streamlit as st
import streamlit_canary as sc
import typing as t
from lk_utils import fs
from .i18n import i18n
from ...venv.target_venv import get_library_root

_state = sc.session.get_state(lambda: {
    'default_venv_dirpath': {}
})


def main(root: str) -> t.Optional[dict]:
    if root not in _state['default_venv_dirpath']:
        _state['default_venv_dirpath'][root] = get_library_root(root)
    
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
                i18n.deps_venv_ask,
                _state['default_venv_dirpath'][root],
                parent=root,
                check=2,
                help=i18n.deps_venv_help
            )
            dir_o = sc.path_input(
                i18n.deps_output_ask, parent=root
            )
            if dir_i and dir_o:
                return {
                    'mode': 'tree_shaking_dependencies',
                    'dir_i': dir_i,
                    'dir_o': dir_o,
                }
