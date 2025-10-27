if __name__ == '__main__':
    __package__ = 'depsland.webui.app_builder'

import re
import streamlit as st
import streamlit_canary as sc
import typing as t
from random import randint
from lk_utils import fs
from uuid import uuid1
from . import assets_picker
from . import dependency_scheme
from .i18n import i18n

_state = sc.session.get_state(lambda: {
    # 'project_to_appid': {},
    'appinfo': {}  # {project_dir: {...}, ...}
}, version=5)


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
    if not (prjdir := sc.path_input(i18n.ask_project_path, check=2)):
        return
    
    if prjdir not in _state['appinfo']:
        x = _state['appinfo'][prjdir] = {
            'appid': _generate_appid(
                (y := fs.basename(prjdir)).lower().replace('-', '_')
            ),
            'version': Version((0, 1, 0))
        }
        print('{} -> {}'.format(y, x))
    info = _state['appinfo'][prjdir]
    
    with st.expander(i18n.appinfo, expanded=True):
        row = st.columns((8, 2), vertical_alignment='bottom')
        with row[0]:
            st.text_input(
                i18n.appid, info['appid'], disabled=True, help=i18n.appid_help
            )
        with row[1]:
            if sc.long_button(i18n.appid_regenerate):
                # _state['appinfo'].pop(prjdir)
                _state['appinfo'][prjdir]['appid'] = _generate_appid(
                    fs.basename(prjdir).lower().replace('-', '_')
                )
                st.rerun()
        
        row = st.columns((8, 2), vertical_alignment='bottom')
        with row[0]:
            st.text_input(i18n.appname, _titlize(fs.basename(prjdir)))
        
        ver: Version = info['version']
        # row = st.columns((35, 15, 15, 15, 20), vertical_alignment='bottom')
        row = st.columns((4, 4, 2), vertical_alignment='bottom')
        with row[1]:
            x = sc.radio(
                i18n.version_switch,
                {
                    'alpha': i18n.version_alpha,
                    'beta': i18n.version_beta,
                    'formal': i18n.version_formal,
                },
                index=2,
                horizontal=True
            )
            match x:
                case 'alpha':
                    ver.to_alpha()
                case 'beta':
                    ver.to_beta()
                case 'formal':
                    ver.to_formal()
        with row[2]:
            if sc.long_button(i18n.version_bump):
                ver.bump()
        with row[0]:
            st.text_input(i18n.version, str(ver))
        
        tabs = st.tabs((i18n.assets_title, i18n.deps_scheme, i18n.enc_title))
        with tabs[0]:
            assets_picker.main(prjdir)
        with tabs[1]:
            dependency_scheme.main(prjdir)


def _generate_appid(basename: str) -> str:
    assert re.fullmatch(r'[a-z]\w*[a-z]', basename), basename
    return '{}_0x{:04x}'.format(basename, randint(0, 0xFFFF))


def _generate_appid_2() -> str:
    return uuid1().hex


def _titlize(name: str) -> str:
    return ' '.join(re.findall(r'[a-z]+', name)).title()


class Version:
    def __init__(
        self, base: t.Tuple[int, int, int], _alpha: int = 0, _beta: int = 0
    ) -> None:
        self._origin = (tuple(base), _alpha, _beta)
        self._base = list(base)
        self._alpha = _alpha
        self._beta = _beta
        self._current_state = ''
    
    def __str__(self) -> str:  # noqa
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
    # strun 2180 depsland/webui/app_builder/main.py
    main()
