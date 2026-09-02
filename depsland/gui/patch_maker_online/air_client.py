import typing as tp

import airmise as air
import streamlit as st
import streamlit_canary as sc


class _State:
    # init: bool
    # air_caller: tp.Optional[air.ProxyCaller]
    air_client: tp.Optional[tp.Union[air.Client, air.ProxyCaller]]
    # connection_hub: air.Client
    # connection_sub: air.Client
    remote_working_dir: str

    def __init__(self) -> None:
        # self.air_caller = None
        self.air_client = None
        self.remote_working_dir = ''

    @property
    def connected(self) -> bool:
        return self.air_client is not None


state = tp.cast(_State, sc.init_state(_State, version=2))


def aircall(func_name: str, *args, **kwargs) -> tp.Any:
    return state.air_client.call(func_name, *args, **kwargs)


def airexec(code: str, **kwargs) -> tp.Any:
    return state.air_client.exec(code, **kwargs)


def close_air_client() -> None:
    if state.air_client:
        state.air_client.close()
        state.air_client = None


def init_air_client(debug: bool = False, **kwargs) -> None:
    if debug:
        state.air_client = air.Client().connect(host='localhost', port=2191)
    else:
        # the incoming url format: http://localhost:2190/?uid=<uid>
        if st.query_params:
            print(st.query_params, ':nv')
            uid = st.query_params['uid']
            state.air_client = air.ProxyCaller(uid).connect(port=2192)
        else:
            st.warning('Invalid query parameter.')
            st.stop()

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

        def download_patch_2(data: bytes, patch_id: str) -> None:
            fs.make_dir('patches/{}'.format(patch_id))
            fs.dump(data, 'patches/{}/assets.zip'.format(patch_id), 'binary')
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
        
        def get_profile() -> dict:
            return fs.load('patches/profile.json')

        assert fs.exist('patches')
        assert fs.exist('patches/profile.json')
        assert fs.exist('python')
        assert fs.exist('source')
        assert fs.exist('source/.depsland/manifest.pkl')
        assert fs.exist('Check Updates.exe')

        return None
        """
    )
