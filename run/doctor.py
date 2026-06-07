import neoprint as np
from argsense import cli
from lk_utils import fs
from lk_utils import dedent


@cli
def main():
    print(
        """
        Make sure the following tools are working:
        - ossutil (`ossutil version`)
        - poetry (`poetry about`)
        - vlang (`v version`)
        """,
        ':r2',
    )


@cli
def check_next_todos():
    def check_depsland_ol():
        last_state = fs.load(
            'run/_doctor_cache/depsland_ol.json',
            default={'app_launcher_mtime': 0},
        )

        mtime_old = last_state['app_launcher_mtime']
        mtime_new = fs.filetime('sidework/mini_launcher/app_launcher.v')
        if mtime_new > mtime_old:
            np.show(
                ':v6',
                dedent(
                    """
                    "sidework/mini_launcher/app_launcher.v" is updated. you 
                    should recompile it to exe.

                    related:

                    ```sh
                    python sidework/mini_launcher/make.py \\
                        tree_shaking_depsland_online_installer -u
                    ```
                    """,
                    4,
                    lstrip=False,
                ),
            )
            # last_state['app_launcher_mtime'] = mtime_new
            # fs.dump(last_state, 'run/_doctor_cache/depsland_ol.json')

        file_size = fs.filesize('resources/depsland-online-installer.zip', str)
        x = fs.load('sidework/mini_launcher/app_launcher.v', 'plain')
        for line in reversed(x.splitlines()):
            if line.lstrip().startswith(
                "println('Downloading depsland online installer"
            ):
                if file_size not in line:
                    np.show(
                        ':v6i',
                        'you need to update the println message about the file '
                        'size to download: ~{}'.format(file_size),
                    )
                    break
        else:
            raise Exception('cannot find target println line!')

    check_depsland_ol()


if __name__ == '__main__':
    cli.run()
