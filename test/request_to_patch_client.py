import airmise as air
from argsense import cli


@cli
def main(uid):
    client = air.ProxyCaller(uid).connect(port=2192)
    client.exec(
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
            # assert fs.exist(file), file
            return fs.load(file, 'binary')
            # with open(file, 'rb') as f:
            #     return f.read()
            # return fs.load('source/run.py')
            # return '123'
            # print(
            #     get_current_working_dir(),
            #     file, 
            #     fs.filesize(file, str), 
            #     (x := fs.load(file, 'binary'))[:100], 
            #     ':nv'
            # )
            # return x

        def get_profile() -> dict:
            return fs.load('patches/profile.json')

        assert fs.exist('patches')
        assert fs.exist('patches/profile.json')
        assert fs.exist('python')
        assert fs.exist('source')
        assert fs.exist('source/.depsland/manifest.pkl')
        assert fs.exist('Check Updates.exe')

        print('cwd', get_current_working_dir())
        print('appid', get_appid())
        print('manifest', len(get_manifest_data() or ''))
        """
    )

    # print(len(client.call('get_manifest_data_2')))
    print(len(client.call('get_manifest_data') or ''))


if __name__ == '__main__':
    cli.run(main)
