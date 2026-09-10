import typing as tp
from argsense import cli
from depsland.api import dev_api
from depsland.utils import bump_version
from lk_utils import fs
from lk_utils import manipulate_text
from neoprint import print


@cli
def project_to_app_standalone(
    profile: str,
    image_key: tp.Literal['src_max', 'src_min', 'enc_max', 'enc_min'],
    new_version: str = '',
    compress_result: bool = False,
) -> None:
    """
    Args:
        image_key (-k):
        new_version (-v):
        compress_result (-c):
    """
    dev_api.build_project(
        profile,
        image_key,
        new_version=new_version,
        compress_result=compress_result,
        publish=1,
    )


@cli
def manifest_to_app_standalone(
    manifest_file: str,
    new_version: str = '',
    # compress_result: bool = False,
) -> None:
    """
    Args:
        new_version (-v):
    """
    manifest_content = fs.load(manifest_file, 'plain')
    old_version = (
        manipulate_text(manifest_content)
        .find('"version": "')
        .then_cut()
        .find('"')
        .slice()
    )
    if new_version == '$keep':
        new_version = old_version
        print(new_version, ':nv2')
    else:
        if new_version == '':
            new_version = bump_version(old_version)
        print('version: {} -> {}'.format(old_version, new_version), ':r2')
        fs.dump(
            (
                manipulate_text(manifest_content)
                .find('"version": "')
                .then_cut()
                .find('"')
                .cut()
                .replace(new_version)
                .output()
            ),
            manifest_file,
            'plain',
        )

    dev_api.build_offline(manifest_file)


if __name__ == '__main__':
    # python run/build_app.py -h
    # python run/build_app.py project_to_app_standalone <profile> enc_max
    # python run/build_app.py manifest_to_app_standalone <manifest_file>
    cli.run()
