import sys
from argsense import cli
from lk_utils import fs
from lk_utils import run_cmd_args
from . import doctor

cli.add_cmd(doctor.main, 'doctor')

@cli
def build_depsland_standalone():
    print('see $[build/build_depsland/main.py].')

@cli
def start_depsland_online_service(bore_secret: str, debug: bool = False):
    from .depsland_online import run_all
    run_all(bore_secret, debug=debug)

@cli
def upload_resource_to_oss(file: str, force: bool = False):
    assert fs.isfile(file)
    run_cmd_args(
        (
            'ossutil', 
            'cp', 
            file,
            'oss://likianta-public-share/depsland-resources/{}'
            .format(fs.basename(file)),
            force and '-f' or '-u',
        ),
        verbose=True
    )

if __name__ == '__main__':
    cli.run()
