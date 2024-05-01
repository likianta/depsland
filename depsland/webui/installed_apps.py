import typing as t

import streamlit as st
from lk_utils import fs

from ..api.user_api import run_app
from ..paths import apps as app_paths


def main() -> None:
    cols = st.columns(2)
    index = -1
    for app_name, vers in list_installed_apps():
        index += 1
        with cols[index % 2]:
            with st.container(border=True):
                st.write(f':blue[**{app_name}**]')
                target_ver = st.selectbox(
                    'Version ({})'.format(len(vers)),
                    vers,
                    key=f'{app_name}_version',
                )
                if st.button(
                    'Run',
                    key=f'run_{app_name}',
                    use_container_width=True,
                ):
                    run_app(app_name, _version=target_ver)


def list_installed_apps() -> t.Iterator[t.Tuple[str, t.List[str]]]:
    for d in fs.find_dirs(app_paths.root):
        if d.name.startswith('.'):
            continue
        if fs.exists(x := f'{d.path}/.inst_history'):
            history = fs.load(x).splitlines()
            yield d.name, history
