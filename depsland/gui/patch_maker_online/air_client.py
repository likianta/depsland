import typing as tp

import airmise as air
import streamlit as st
import streamlit_canary as sc


class _State:
    # air_client: tp.Optional[tp.Union[air.Client, air.ProxyCaller]]
    air_client: tp.Optional[air.ProxyCaller]
    client_id: str
    # remote_working_dir: str

    def __init__(self) -> None:
        self.air_client = None
        self.client_id = ''

    @property
    def connected(self) -> bool:
        return self.air_client is not None


state = tp.cast(_State, sc.init_state(_State, version=19))


def aircall(func_name: str, *args, **kwargs) -> tp.Any:
    return state.air_client.call(func_name, *args, **kwargs)


def airexec(code: str, **kwargs) -> tp.Any:
    return state.air_client.exec(code, **kwargs)


def check_init(debug: bool = False) -> tp.Tuple[str, bool]:
    old_id = state.client_id
    if debug or not st.query_params:
        with sc.row('bottom'):
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
        state.air_client.close(peer_close=True)
        state.air_client = None
        state.client_id = ''


def init_air_client(client_id: str) -> None:
    state.air_client = air.ProxyCaller(client_id).connect(port=2192)
    _init_remote_env(state.air_client)
    # state.remote_working_dir = aircall('get_current_working_dir')
    # print(state.remote_working_dir, ':n')


def _init_remote_env(air_client: air.ProxyCaller) -> None:
    air_client.exec(
        """
        # fixup for legacy versions
        import os
        from lk_utils import dedent, fs, uuid

        if os.getcwd().endswith('source'):
            proj_dir = fs.parent(os.getcwd())
        else:
            proj_dir = fs.normpath(os.getcwd())
        
        if not fs.exist('{}/patches/initial_manifest.pkl'.format(proj_dir)):
            fs.copy_file(
                '{}/source/.depsland/manifest.pkl'.format(proj_dir),
                '{}/patches/initial_manifest.pkl'.format(proj_dir),
            )
        
        if not fs.exist(
            '{}/source/.depsland/mini_deps/depsland_updater/__main__.py'
            .format(proj_dir)
        ):
            fs.dump(
                dedent(
                    '''
                    from argsense import cli
                    from .patch_client import patch_online
                    cli.add_cmd(patch_online)
                    if __name__ == '__main__':
                        cli.run()
                    '''
                ),
                '{}/source/.depsland/mini_deps/depsland_updater/__main__.py'
                .format(proj_dir),
                'plain',
            )
        
        # _chk_uid = uuid(
        #     fs.load('{}/Check Updates.exe'.format(proj_dir), 'binary')
        # )[::4]

        # def get_check_updates_version() -> str:
        #     return _chk_uid

        # def replace_check_updates_exe(raw: bytes) -> None:
        #     fs.copy_file(
        #         '{}/Check Updates.exe'.format(proj_dir),
        #         '{}/Check Updates (Deprecated {}).exe'
        #         .format(proj_dir, _chk_uid),
        #     )
        #     fs.dump(raw, '{}/Check Updates.exe'.format(proj_dir), 'binary')
        """
    )

    air_client.exec(
        """
        import os
        import sys
        from lk_utils import fs
        from time import sleep

        if os.getcwd().endswith('source'):
            proj_dir = fs.parent(os.getcwd())
        else:
            proj_dir = fs.normpath(os.getcwd())
        assert fs.exist('{}/patches'.format(proj_dir))
        assert fs.exist('{}/patches/initial_manifest.pkl'.format(proj_dir))
        assert fs.exist('{}/patches/profile.json'.format(proj_dir))
        assert fs.exist('{}/python'.format(proj_dir))
        assert fs.exist('{}/source'.format(proj_dir))
        assert fs.exist('{}/Check Updates.exe'.format(proj_dir))

        def download_patch(url: str, patch_id: str) -> None:
            fs.make_dir('{}/patches/{}'.format(proj_dir, patch_id))
            fs.download(
                url, 
                '{}/patches/{}/assets.zip'.format(proj_dir, patch_id), 
                progress=True
            )
            profile = get_profile()
            profile['latest_patch'] = patch_id
            fs.dump(profile, '{}/patches/profile.json'.format(proj_dir))

        def download_patch_2(
            data1: bytes, data2: bytes, data3: bytes, patch_id: str
        ) -> None:
            patch_dir = '{}/patches/{}'.format(proj_dir, patch_id)
            fs.make_dir(patch_dir)
            fs.dump(data1, '{}/assets.zip'.format(patch_dir), 'binary')
            fs.dump(data2, '{}/assets_map.json'.format(patch_dir), 'binary')
            fs.dump(data3, '{}/manifest.pkl'.format(patch_dir), 'binary')
            
            profile['latest_patch'] = patch_id
            fs.dump(profile, '{}/patches/profile.json'.format(proj_dir))

        def get_appid() -> str:
            return profile['appid']

        # def get_current_working_dir() -> str:
        #     return fs.normpath(os.getcwd())
        
        def get_manifest_data(
            # file: str = '{}/source/.depsland/manifest.pkl'.format(proj_dir)
        ) -> bytes:
            if profile['current_patch']:
                file = '{}/patches/{}/manifest.pkl'.format(
                    proj_dir, profile['current_patch']
                )
            else:
                # file = '{}/source/.depsland/manifest.pkl'.format(proj_dir)
                file = '{}/patches/initial_manifest.pkl'.format(proj_dir)
            print('current manifest file', file)
            # transmit the raw data (bytes) to server.
            assert fs.exist(file), file
            return fs.load(file, 'binary')

        def get_profile() -> dict:
            return fs.load('{}/patches/profile.json'.format(proj_dir))

        profile = get_profile()
        """
    )
