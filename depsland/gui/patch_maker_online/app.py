"""
Docs:
    - wiki/src/devnote/patch-maker-workflow.md
    - wiki/src/devnote/difference-between-setup-wizard-and-patch-maker.md
"""

if not __package__:
    __package__ = 'depsland.gui.patch_maker_online'

import typing as tp
from functools import partial

import streamlit as st
import streamlit_canary as sc
from argsense import cli
from lk_utils import fs
from lk_utils import run_cmd_args
from lk_utils import uuid
from neoprint import format
from neoprint import print

from . import air_client as air
from .logic import analyze_assets_diff
from .logic import create_patch_id
from .logic import generate_patch_result
from .logic import load_current_manifest
from .logic import reload_user_manifest
from ... import paths
from ...manifest import T as T0
from ...manifest import diff_manifest
from ...manifest import dump_manifest
from ...manifest import load_manifest
from ...utils import make_temp_dir


class T:
    AssetInfo = T0.AssetInfo
    AssetsMap = tp.Dict[
        str, tp.Tuple[tp.Optional[T0.AbsPath], T0.RelPath, bool, int, T0.Action]
        # ^ file_id   ^ src_abspath, dst_relpath, isdir, size, action
        #   notice: AssetsMap is order sensitive: the "delete" action must be
        #   first. because if we have both `append:A` and `delete:A/B`, latter
        #   delete will make loss to append action.
    ]
    Manifest = T0.ManifestObject
    TableData = tp.List[tp.Tuple[str, ...]]


class _State:
    # accepted_keys: tp.Iterable[str]
    appid_to_project_path: tp.Dict[str, str]
    assets_dir: str
    assets_map: tp.Optional[T.AssetsMap]
    assets_map_generation: int
    filtered_assets_map: tp.Optional[T.AssetsMap]
    # init: bool
    new_manifest: T.Manifest
    old_manifest: T.Manifest
    patch_id: str
    registered_project_paths: tp.Tuple[str, ...]
    # table_diff_data: tp.Optional[T.TableData]
    target_project_path: str
    # user_manifest: tp.Optional[dict]
    user_manifest_file: str  # always local path
    # _filtered_assets_map: tp.Optional[T.AssetsMap]

    def __init__(self) -> None:
        self.registered_project_paths = ()
        self.appid_to_project_path = fs.load(
            fs.here('_appid_to_project.yaml'), default=dict
        )
        # self.user_manifest_file = 'test/_example_manifest.pkl'
        self.assets_map = None
        self.assets_map_generation = 0
        self.filtered_assets_map = None
        # self.table_diff_data = None


state = tp.cast(_State, sc.init_state(_State, version=34))


@cli
def main(
    debug: bool = False, developer_mode: bool = False, local_test: bool = False
) -> None:
    st.set_page_config('Depsland Patch Maker Online')
    if developer_mode:
        st.title(':red[Depsland Patch Maker]')
    else:
        st.title('Depsland Patch Maker')

    if not air.state.air_client and not local_test:
        client_id, air_init = air.check_init(debug=debug)
        if not air_init:
            if client_id:
                air.init_air_client(client_id=client_id)
                # remote to local
                if debug:
                    state.user_manifest_file = 'test/_example_manifest.pkl'
                else:
                    state.user_manifest_file = fs.here('_user_manifest.pkl')
                    #   TODO: use `paths.temp.user_manifest_pkl` path.
                assert air.aircall('get_manifest_data') is not None  # TEST
                fs.dump(
                    air.aircall('get_manifest_data'),
                    state.user_manifest_file,
                    'binary',
                )

                # locate project path
                # state.user_manifest = fs.load(state.user_manifest_file)
                state.target_project_path = state.appid_to_project_path[
                    appid := air.aircall('get_profile')['appid']
                ]
                print(appid, state.target_project_path, ':n')
            else:
                return

    with st.container(border=True):
        if local_test:
            if x := _local_test_manifests():
                state.old_manifest, state.new_manifest = x
        else:
            st.markdown('Project path: `{}`'.format(state.target_project_path))
            file0 = st.text_input(
                'User manifest file', state.user_manifest_file
            )
            file1 = st.text_input(
                'Latest manifest file', _auto_find_latest_manifest_file(appid)
            )

    main_button_row = sc.row()
    stat_area = st.empty()
    with main_button_row:
        if st.button('Analyze manifest', type='primary'):
            if not local_test:
                assert file0 and file1
                state.old_manifest = load_manifest(
                    file0, state.target_project_path
                )
                state.new_manifest = load_manifest(
                    file1, state.target_project_path
                )
            state.patch_id = create_patch_id(
                state.new_manifest['appid'],
                state.old_manifest['version'],
                state.new_manifest['version'],
            )
            state.assets_map = analyze_assets_diff(
                state.old_manifest, state.new_manifest
            )
            state.assets_map_generation += 1

        if st.button('Generate patch result', type='secondary'):
            assets_map = state.filtered_assets_map or state.assets_map
            assert assets_map
            state.assets_dir = generate_patch_result(state.patch_id, assets_map)
            
            if local_test:
                patch_exe = _generate_patch_executable(
                    assets_map, state.assets_dir, state.patch_id
                )
                with stat_area:
                    st.success(
                        'Patch executable generated: `{}` ({})'.format(
                            patch_exe, fs.filesize(patch_exe, str)
                        )
                    )

        if developer_mode:
            if st.button('Save assets diff'):
                appid = state.new_manifest['appid']
                old_ver = state.old_manifest['version']
                new_ver = state.new_manifest['version']

                ov = fs.load(paths.chore.overview, default=dict)
                if appid not in ov:
                    ov[appid] = {}
                if old_ver not in ov[appid]:
                    ov[appid][old_ver] = []
                ov[appid][old_ver].append(new_ver)

                simplified_assets_map = {}
                for k, (
                    abspath,
                    relpath,
                    is_dir,
                    size,
                    action,
                ) in assets_map.items():
                    simplified_assets_map[k] = '{}:{}{}'.format(
                        relpath,
                        '1' if is_dir else '0',
                        '0' if size == -1 else '1',
                        # format: `<relpath>:<is_dir><action>`
                        #   action: 1 for append/update, 0 for delete.
                    )
                file = '{}/{}-to-{}.json'.format(
                    paths.chore.patch_diff, old_ver, new_ver
                )
                fs.dump(simplified_assets_map, file)
                fs.dump(ov, paths.chore.overview)

                with stat_area:
                    st.success(
                        'Assets diff saved: `{}` ({})'.format(
                            file, fs.filesize(file, str)
                        )
                    )

        if not local_test:
            if st.button('Push patch to client'):
                with stat_area:
                    with st.spinner('Working...'):
                        _push_patch_to_client(
                            tp.cast(
                                T.AssetsMap,
                                state.filtered_assets_map or state.assets_map,
                            ),
                            state.assets_dir,
                            state.patch_id,
                        )

    if state.assets_map:
        with main_button_row:
            st.space('stretch')
            with st.popover('Custom filter'):
                with st.container(width=500):
                    state.filtered_assets_map = _custom_filter(state.assets_map)
            # sort_by = st.radio('Sort by', ('native', 'size'), horizontal=True)
            sort_by_size = sc.toggle_button('Sort by size', True)
        _preview_assets_diff(
            state.assets_map, 'size' if sort_by_size else 'native'
        )

    if developer_mode and not local_test:
        with st.bottom:
            _debug_tool()


def _custom_filter(assets_map: T.AssetsMap) -> T.AssetsMap:
    all_keys = frozenset(assets_map.keys())
    incremental_keys = frozenset(x for x in all_keys if assets_map[x][3] != -1)
    decremental_keys = all_keys - incremental_keys
    excluded_keys = st.multiselect(
        'Select assets to be excluded',
        sorted(incremental_keys, key=lambda k: assets_map[k][3], reverse=True),
        format_func=lambda k: '{} ({})'.format(
            assets_map[k][1], fs.pretty_size(assets_map[k][3], sep='')
        ),
        # accept_new_options=True,  # TODO: support glob pattern
        key='_:custom_filter:{}'.format(state.assets_map_generation),
    )

    if st.button('Apply', width='stretch', disabled=not excluded_keys):
        total_size = sum(assets_map[k][3] for k in incremental_keys)
        excluded_size = sum(assets_map[k][3] for k in excluded_keys)
        remaining_size = total_size - excluded_size
        st.table(
            {
                'Total items': str(len(incremental_keys)),
                'Total size': fs.pretty_size(total_size, sep=' '),
                'Excluded items': sc.red(len(excluded_keys)),
                'Excluded size': sc.red(fs.pretty_size(excluded_size, sep=' ')),
                'Remaining items': sc.green(
                    len(incremental_keys) - len(excluded_keys)
                ),
                'Remaining size': sc.green(
                    fs.pretty_size(remaining_size, sep=' ')
                ),
            }
        )

    if excluded_keys:
        final_keys = (
            *sorted(decremental_keys),
            #   delete actions go first. see reason in `T.AssetsMap:comment`.
            *sorted(incremental_keys - frozenset(excluded_keys)),
        )
        return {k: assets_map[k] for k in final_keys}
    else:
        return assets_map


def _debug_tool() -> None:
    if air.state.air_client:
        if st.button(
            ':red[Close client]', disabled=not bool(air.state.air_client)
        ):
            air.close_air_client()
            st.rerun()
    else:
        if st.button(
            ':green[Start client]', disabled=bool(air.state.air_client)
        ):
            assert air.state.client_id
            air.init_air_client(air.state.client_id)
            st.rerun()


def _local_test_manifests() -> tp.Optional[tp.Tuple[T.Manifest, T.Manifest]]:
    if not state.registered_project_paths:
        state.registered_project_paths = fs.load(
            fs.here('_project_paths.yaml'), default=()
        )
    proj_path = st.selectbox('Select project', state.registered_project_paths)
    old_manifest_path = st.text_input(
        'Old manifest file', key='local_test:old_manifest_path:input'
    )
    with sc.row('bottom'):
        new_manifest_path = st.text_input(
            'New manifest file', key='local_test:new_manifest_path:input'
        )

        def _swap_path(clear: bool) -> None:
            _ = st.session_state['local_test:old_manifest_path:input']
            b = st.session_state['local_test:new_manifest_path:input']
            st.session_state['local_test:old_manifest_path:input'] = b
            st.session_state['local_test:new_manifest_path:input'] = (
                '' if clear else b
            )

        st.button(
            ':material/arrow_circle_up:',
            help='Swap path and clear this field.',
            disabled=not new_manifest_path,
            on_click=partial(_swap_path, clear=True),
        )

        st.button(
            ':material/arrows_up_down_circle:',
            help='Duplicate new manifest path.',
            disabled=not new_manifest_path,
            on_click=partial(_swap_path, clear=False),
        )

    if (
        old_manifest_path
        and new_manifest_path
        and new_manifest_path != old_manifest_path
        and fs.exist(old_manifest_path)
        and fs.exist(new_manifest_path)
    ):
        return load_manifest(old_manifest_path, proj_path), load_manifest(
            new_manifest_path, proj_path
        )
    else:
        return None


def _preview_assets_diff(assets_map: T.AssetsMap, sort_by: str = 'native'):
    table_data = [('Index', 'Action', 'RelPath', 'Size')]
    if sort_by == 'native':
        keys = assets_map.keys()
    elif sort_by == 'size':
        keys = sorted(
            assets_map.keys(),
            key=lambda k: (
                0 if assets_map[k][3] == -1 else 1,
                assets_map[k][3],
            ),
            reverse=True,
        )
    else:
        raise Exception(sort_by)
    for i, k in enumerate(keys, 1):
        _, relpath, is_dir, size, action = assets_map[k]
        action_label = (
            ':green[APPEND]'
            if action == 'append'
            else ':yellow[UPDATE]'
            if action == 'update'
            else ':red[DELETE]'
        )
        icon = (
            ':orange[:material/folder:]'
            if is_dir
            else ':blue[:material/description:]'
        )
        table_data.append(
            (
                str(i),
                action_label,
                icon + ' ' + relpath,
                'N/A' if size == -1 else fs.pretty_size(size, sep=' '),
            )
        )
    st.table(table_data)


# ------------------------------------------------------------------------------


# FIXME or DELETE
def _apply_patch(assets_map: T.AssetsMap, used_keys: tp.Iterable[str]):
    temp_dir = make_temp_dir()
    for k in used_keys:
        abspath, relpath, is_dir, size, action = assets_map[k]
        relpath = 'source/' + relpath
        if action == 'delete' or action == 'update':
            if is_dir:
                air.airexec('fs.remove_tree(path)', path=relpath)
            else:
                air.airexec('fs.remove_file(path)', path=relpath)
        if action == 'append' or action == 'update':
            assert abspath
            if is_dir:
                fs.zip(abspath, '{}/{}.zip'.format(temp_dir, k))
                air.aircall(
                    'fs.dump(bytes_i, path_m)\nfs.unzip(path_m, path_o)',
                    bytes_i=fs.load('{}/{}.zip'.format(temp_dir, k), 'binary'),
                    path_m=relpath + '.zip',
                    path_o=relpath,
                )
            else:
                air.aircall(
                    'fs.dump(bytes_i, path_o)',
                    bytes_i=fs.load(abspath, 'binary'),
                    path_o=relpath,
                )


def _auto_find_latest_manifest_file(appid: str) -> str:
    proj_dir = state.appid_to_project_path[appid]
    pyproj_data = fs.load('{}/pyproject.toml'.format(proj_dir))
    latest_version = pyproj_data['project']['version']
    dist_dir = '{}/dist/{}-{}'.format(proj_dir, appid, latest_version)
    if fs.exist(dist_dir):
        assert fs.exist('{}/patches/initial_manifest.pkl'.format(dist_dir))
        return '{}/patches/initial_manifest.pkl'.format(dist_dir)
    return ''


def _push_patch_to_client(
    assets_map: T.AssetsMap, assets_dir: str, patch_id: str
):
    """
    TODO:
        - provide a download url.
        - multi-thread download.
    """

    simplified_assets_map = {}
    for k, (abspath, relpath, is_dir, size, action) in assets_map.items():
        simplified_assets_map[k] = '{}:{}{}'.format(
            relpath,
            '1' if is_dir else '0',
            '0' if size == -1 else '1',
            # format: `<relpath>:<is_dir><action>`
            #   action: 1 for append/update, 0 for delete.
        )

    # `build/exe/check_updates.v` requires the following three files.
    fs.dump(simplified_assets_map, paths.chore.assets_map)
    fs.zip(assets_dir, paths.chore.assets_zip, True, progress=True)
    dump_manifest(state.new_manifest, paths.chore.manifest_pkl)

    air.aircall(
        'download_patch_2',
        data1=fs.load(paths.chore.assets_zip, 'binary'),
        data2=fs.load(paths.chore.assets_map, 'binary'),
        data3=fs.load(paths.chore.manifest_pkl, 'binary'),
        patch_id=patch_id,
    )


if __name__ == '__main__':
    # production:
    #   strun 2190 depsland/gui/patch_maker_online/app.py
    # debug:
    #   python -m airmise run_server --port 2192
    #   strun 2190 depsland/gui/patch_maker_online/app.py -- --debug
    #       --developer-mode --client-host localhost --client-port 2192
    # local test:
    #   strun 2190 depsland/gui/patch_maker_online/app.py -- --debug
    #       --developer-mode --local-test
    cli.run(main)
