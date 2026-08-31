import typing as tp

import airmise as air
import streamlit as st
import streamlit_canary as sc


@sc.init_state
class State:
    air_client: tp.Optional[air.Client] = None
    current_working_dir: str = ''


def aircall(func_name: str, *args, **kwargs) -> tp.Any:
    return State.air_client.call(func_name, *args, **kwargs)


def airexec(code: str, **kwargs) -> tp.Any:
    return State.air_client.exec(code, **kwargs)


def close_air_client() -> None:
    if State.air_client:
        State.air_client.close()
        State.air_client = None


def init_air_client(debug: bool = False, **kwargs) -> None:
    if debug:
        client_host = kwargs['client_host']
        client_port = kwargs['client_port']
    else:
        # the incoming url for example:
        #   http://localhost:2190/?ip=172.20.128.101&port=2193
        if st.query_params:
            print(st.query_params, ':n')
            client_host = st.query_params['ip']
            client_port = int(st.query_params['port'])
        else:
            st.warning('Invalid query parameter.')
            st.stop()

    State.air_client = air.Client().open(client_host, client_port)

    _init_remote_env()
    State.current_working_dir = aircall('get_current_working_dir')


def _init_remote_env() -> None:
    State.air_client.exec(
        """
        import os
        import sys
        from lk_utils import fs
        from time import sleep

        def get_current_working_dir() -> str:
            return os.getcwd()
        
        # def get_manifest_data(file: str = '') -> bytes:
        def get_manifest_data(file: str) -> bytes:
            # transmit the raw data (bytes) to server.
            # if not file:
            #     file = fs.here('source/.depsland/manifest.pkl')
            assert fs.exist(file), file
            return fs.load(file, 'binary')
        
        return None
        """
    )
