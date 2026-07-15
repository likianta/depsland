"""
TODO: implement this prototype as `patch_extractor.go` in Go language.

when user downloads a patch_extractor.exe, they should put it in this place:
    $gui
    |= python                   # user python interpreter, version 3.12
    |= source                   # user source files
    |= patches                  # user should put their patches here
        |- patch_extractor.exe  # <- here
    |- Hello World.exe          # user launcher
    |- Hello World (Debug).exe  # user launcher with debug mode
"""

import json
import os
import shutil
import zipfile


def main() -> None:
    patch_id = 'c32a7f82869746729205e5153065ecbd'

    assets_map_file = 'grocery/assets_map.json'
    assets_zip_file = 'grocery/assets.zip'
    #   note: in go version, assets_file should be embedded in the binary.

    # TODO: extract embed data to local files
    extracted_dir = './{}'.format(patch_id)
    if os.path.exists(extracted_dir):
        shutil.rmtree(extracted_dir)
    os.mkdir(extracted_dir)
    shutil.copyfile(assets_map_file, '{}/assets_map.json'.format(extracted_dir))
    shutil.copyfile(assets_zip_file, '{}/assets.zip'.format(extracted_dir))
    with zipfile.ZipFile('{}/assets.zip'.format(extracted_dir), 'r') as zip_ref:
        zip_ref.extractall(extracted_dir)
    os.mkdir('{}/backups'.format(extracted_dir))

    # load assets map
    with open('{}/assets_map.json'.format(extracted_dir), 'r') as f:
        assets_map = json.load(f)
        # {file_id: [src_abspath, dst_relpath, append_or_delete], ...}
        #   file_id: str.
        #   src_abspath: str, not used in this case.
        #   dst_relpath: str, relative path starts from "source".
        #   append_or_delete: bool, True if append/update, False if delete.

    # apply patch
    for file_id, v in assets_map.items():
        file_i = '{}/assets/{}'.format(extracted_dir, file_id)
        file_m = '{}/backups/{}'.format(extracted_dir, file_id)
        file_o = 'source/{}'.format(v[1])
        if v[2]:  # append/update
            assert os.path.exists(file_i)
            if os.path.exists(file_o):  # update
                shutil.move(file_o, file_m)
                shutil.move(file_i, file_o)
            else:  # append
                shutil.move(file_i, file_o)
        else:  # delete
            os.move(file_o, file_m)

    # generate new manifest
    ...  # TODO: currently not supported


if __name__ == '__main__':
    main()
