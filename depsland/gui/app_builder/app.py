if __name__ == '__main__':
    __package__ = 'depsland.gui.app_builder'

import re
import typing as tp
from uuid import uuid4

import streamlit as st
import streamlit_canary as sc
from lk_utils import fs

from . import assets_picker
from . import dependency_scheme
from .i18n import i18n

_state = sc.init_state(
    lambda: {
        'appinfo': {},  # {project_dir: {...}, ...}
        'current_project_dir': '',
        # 'project_to_appid': {},
    },
    version=6,
)


def main() -> None:
    """
    params:
        server_mode:
            this ui can either run in server mode or client mode.
            we recommend user who wants to have a try to depsland to use -
            server mode.
            but for security and performance reasons, user should download and -
            run in client mode to build their formal productions.
    """
    st.title(i18n.title)
    st.markdown(i18n.proj_desc)

    if prjdir := sc.path_input(i18n.ask_proj_path, check=2):
        _state['current_project_dir'] = prjdir
    else:
        return

    if prjdir not in _state['appinfo']:
        _state['appinfo'][prjdir] = {
            'appid': _generate_appid(),
            'version': Version((0, 1, 0)),
        }
    info = _state['appinfo'][prjdir]

    with st.expander(i18n.appinfo, expanded=True):
        with sc.row('bottom'):
            st.text_input(i18n.appname, _titlize(fs.basename(prjdir)), width=240)
            st.text_input(
                i18n.appid, info['appid'], disabled=True, help=i18n.appid_help
            )
            if st.button(i18n.appid_regenerate, width=120):
                # _state['appinfo'].pop(prjdir)
                _state['appinfo'][prjdir]['appid'] = _generate_appid()
                st.rerun()

        ver: Version = info['version']
        with sc.row('bottom'):
            place1 = st.empty()
            x = sc.radio(
                i18n.version_switch,
                {
                    'alpha': i18n.version_alpha,
                    'beta': i18n.version_beta,
                    'formal': i18n.version_formal,
                },
                index=2,
                horizontal=True,
                width='stretch',
            )
            match x:
                case 'alpha':
                    ver.to_alpha()
                case 'beta':
                    ver.to_beta()
                case 'formal':
                    ver.to_formal()
            if st.button(i18n.version_bump, width=120):
                ver.bump()
            with place1:
                st.text_input(i18n.version, str(ver), width=240)

        tabs = st.tabs(
            (
                i18n.tab_title_1_assets,
                i18n.tab_title_2_deps_scheme,
                i18n.tab_title_3_enc,
            )
        )
        with tabs[0]:
            assets_picker.main(prjdir)
        with tabs[1]:
            dependency_scheme.main(prjdir)
    
    with st.bottom:
        st.button(i18n.start_building, type='primary', width='stretch')  # TODO


def _generate_appid() -> str:
    return uuid4().hex


def _titlize(name: str) -> str:
    return ' '.join(re.findall(r'[a-z]+', name)).title()


class Version:
    def __init__(
        self, base: tp.Tuple[int, int, int], _alpha: int = 0, _beta: int = 0
    ) -> None:
        self._origin = (tuple(base), _alpha, _beta)
        self._base = list(base)
        self._alpha = _alpha
        self._beta = _beta
        self._current_state = ''

    def __str__(self) -> str:  # type: ignore
        match self._current_state:
            case '':
                return '{}.{}.{}'.format(*self._base)
            case 'a':
                return '{}.{}.{}a{}'.format(*self._base, self._alpha)
            case 'b':
                return '{}.{}.{}b{}'.format(*self._base, self._beta)

    def bump(self) -> str:
        match self._current_state:
            case '':
                self._base[2] += 1
                self._alpha = self._beta = 0
            case 'a':
                self._alpha += 1
            case 'b':
                self._beta += 1
        return str(self)

    def reset(self) -> str:
        self._base = list(self._origin[0])
        self._alpha, self._beta = self._origin[1:]
        return str(self)

    def to_alpha(self) -> str:
        self._current_state = 'a'
        return '{}.{}.{}a{}'.format(*self._base, self._alpha)

    def to_beta(self) -> str:
        self._current_state = 'b'
        return '{}.{}.{}b{}'.format(*self._base, self._beta)

    def to_formal(self) -> str:
        self._current_state = ''
        return '{}.{}.{}'.format(*self._base)


if __name__ == '__main__':
    # strun 2180 depsland/gui/app_builder/app.py
    main()
