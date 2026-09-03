import typing as tp

import airmise as air
import streamlit as st
import streamlit_canary as sc


class _State:
    # init: bool
    # air_caller: tp.Optional[air.ProxyCaller]
    air_client: tp.Optional[tp.Union[air.Client, air.ProxyCaller]]
    client_id: str
    # connection_hub: air.Client
    # connection_sub: air.Client
    remote_working_dir: str

    def __init__(self) -> None:
        # self.air_caller = None
        self.air_client = None
        self.client_id = ''
        self.remote_working_dir = ''

    @property
    def connected(self) -> bool:
        return self.air_client is not None


state = tp.cast(_State, sc.init_state(_State, version=11))


def aircall(func_name: str, *args, **kwargs) -> tp.Any:
    return state.air_client.call(func_name, *args, **kwargs)


def airexec(code: str, **kwargs) -> tp.Any:
    return state.air_client.exec(code, **kwargs)


def check_init(debug: bool = False) -> tp.Tuple[str, bool]:
    old_id = state.client_id
    if debug or not st.query_params:
        with sc.row():
            new_id = st.text_input(':red[Enter client ID]')
            if debug:
                if st.button('Force refresh', disabled=not new_id):
                    return new_id, False
    else:
        # the incoming url format: http://localhost:2190/?uid=<uid>
        new_id = st.query_params['uid']

    if old_id:
        if new_id:
            return new_id, new_id == old_id
        else:
            return old_id, True
    elif new_id:
        return new_id, False
    else:
        return '', False


def close_air_client() -> None:
    if state.air_client:
        state.air_client.close()
        state.air_client = None


def init_air_client(*, client_id: str, debug: bool = False, **kwargs) -> None:
    if debug:
        state.air_client = air.Client().connect(host='localhost', port=2191)
    else:
        state.air_client = air.ProxyCaller(client_id).connect(port=2192)
    _init_remote_env(state.air_client)
    state.remote_working_dir = aircall('get_current_working_dir')
    print(state.remote_working_dir, ':n')


def _init_remote_env(air_client: tp.Union[air.Client, air.ProxyCaller]) -> None:
    air_client.exec(
        """
        import os
        import sys
        from lk_utils import fs
        from time import sleep

        def download_patch(url: str, patch_id: str) -> None:
            fs.make_dir('patches/{}'.format(patch_id))
            fs.download(
                url, 'patches/{}/assets.zip'.format(patch_id), progress=True
            )
            profile = get_profile()
            profile['latest_patch'] = patch_id
            fs.dump(profile, 'patches/profile.json')

        def download_patch_2(
            data1: bytes, data2: bytes, data3: bytes, patch_id: str
        ) -> None:
            patch_dir = 'patches/{}'.format(patch_id)
            fs.make_dir(patch_dir)
            fs.dump(data1, '{}/assets.zip'.format(patch_dir), 'binary')
            fs.dump(data2, '{}/assets_map.json'.format(patch_dir), 'binary')
            fs.dump(data3, '{}/manifest.pkl'.format(patch_dir), 'binary')
            
            profile = get_profile()
            profile['latest_patch'] = patch_id
            fs.dump(profile, 'patches/profile.json')

        def get_appid() -> str:
            return get_profile()['appid']

        def get_current_working_dir() -> str:
            return fs.normpath(os.getcwd())
        
        def get_manifest_data(
            file: str = 'source/.depsland/manifest.pkl'
        ) -> bytes:
            # transmit the raw data (bytes) to server.
            assert fs.exist(file), file
            return fs.load(file, 'binary')

        assert get_manifest_data() is not None  # TEST
        
        def get_profile() -> dict:
            return fs.load('patches/profile.json')

        assert fs.exist('patches')
        assert fs.exist('patches/profile.json')
        assert fs.exist('python')
        assert fs.exist('source')
        assert fs.exist('source/.depsland/manifest.pkl')
        assert fs.exist('Check Updates.exe')
        """
    )
