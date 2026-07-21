if __name__ == '__main__':
    __package__ = 'depsland.api.dev_api'
    from neoprint import print

import re
import typing as tp

from lk_utils import fs
from lk_utils import slice

from .build_offline import build as build_offline
from .build_offline_2 import build_stripped_offline
from .publish import publish as publish_to_oss
from ...manifest import load_manifest
from ...paths import temp as temp_paths
from ...utils import bump_version as bump_least_version
from ...verspec import compare_version


class T:
    ImageKey = tp.Literal['src_max', 'src_min', 'enc_max', 'enc_min']
    Path = str  # any path form
    Config = tp.TypedDict(
        'Config',
        {
            'root': Path,
            'version': str,
            # the version_bumps:keys are order sensitive. the first key will be
            # treated as primary key.
            # usually the primary key indicates to "pyproject.toml" file.
            'version_bumps': tp.Dict[Path, str],
            'images': tp.TypedDict(
                'Images',
                {
                    'src_max': tp.Union[Path, dict],
                    'src_min': tp.Union[Path, dict],
                    'enc_max': tp.Union[Path, dict],
                    'enc_min': tp.Union[Path, dict],
                },
            ),
        },
    )


def build(
    file: T.Path,
    image_key: T.ImageKey = 'src_min',
    new_version: str = '',
    publish: int = 0,
    remain_last_version: bool = False,
    remove_depsland: bool = True,
    compress_result: bool = False,
) -> T.Config:
    """
    params:
        image_key (-k): suggest 'src_min' or 'enc_max'.
        new_version (-v):
        publish (-p):
            0: do not publish.
            1: generate a standalone package, you can manually publish it, or -
            share it with others by local area network.
            2: generate a standalone package, and publish it via depsland -
            official server.
            tip: if you set `minify_deps` other than 0, we recommend setting -
            this option 1 or 0.
        remove_depsland (-r):
        compress_result (-z): if true, compress to ".7z" format.
            this option is only valid when `publish==1`.
    """
    config = load_config(file)

    curr_version = config['version']
    if remain_last_version:
        print(':v6', 'use last time updated version', curr_version)
        new_version = curr_version
    else:
        if not new_version:
            new_version = bump_least_version(curr_version)
        print(':r2', 'bump version: {} -> {}'.format(curr_version, new_version))
        bump_version_inplaces(
            *config['version_bumps'].keys(), new_version=new_version
        )

    image_file = config['images'][image_key]
    assert image_file, image_key

    if publish == 0:
        load_manifest(image_file)  # make tree-shaking and encryption work.
    elif publish == 1:
        if remove_depsland:
            dir_o = build_stripped_offline(image_file)
        else:
            dir_o = build_offline(image_file)
        if compress_result:
            fs.zip(
                dir_o,
                dst='.7z',
                overwrite=False,
                progress=True,
                compression_level='maximum',
            )
    elif publish == 2:
        publish_to_oss(image_file, upload_dependencies=True)

    config['last_version'] = curr_version  # type: ignore
    config['version'] = new_version
    return config


def bump_version_inplaces(*files: T.Path, new_version: str) -> None:
    for f in files:
        print(':v', f)
        content_r: str = fs.load(f, 'plain')
        match fs.basename(f):
            case '__init__.py':
                content_w = (
                    slice(content_r)
                    .find("__version__ = '")
                    .end()
                    .cut()
                    .find("'")
                    .cut()
                    .inplace(new_version)
                    .out()
                )
            case 'pyproject.toml':
                content_w = (
                    slice(content_r)
                    .find('version = "')
                    .end()
                    .cut()
                    .find('"')
                    .cut()
                    .inplace(new_version)
                    .out()
                )
            case x if x.endswith('.json'):
                content_w = (
                    slice(content_r)
                    .find('"version": "')
                    .end()
                    .cut()
                    .find('"')
                    .cut()
                    .inplace(new_version)
                    .out()
                )
            case x if x.endswith('.yaml'):
                content_w = (
                    slice(content_r)
                    .find('version: ')
                    .end()
                    .cut()
                    .find('\n')
                    .cut()
                    .inplace(new_version)
                    .out()
                )
            case _:
                raise Exception(f)
        assert content_w != content_r, (f, new_version)
        fs.dump(content_w, f, 'plain')


def load_config(file: T.Path) -> T.Config:
    data0: T.Config = fs.load(file)

    root = fs.abspath('{}/{}'.format(fs.parent(file), data0['root']))

    def abspath(x: str) -> T.Path:
        assert x
        return '{}/{}'.format(root, x)

    version = data0.get('version', '')
    if version == '$pyproject_version':
        version = fs.load('{}/pyproject.toml'.format(root))['project'][
            'version'
        ]
    version_bumps = {}
    for k, v in data0.get('version_bumps', {}).items():
        version_bumps[abspath(k)] = v
    if not version:
        # deduce version from places
        assert version_bumps
        for first_item in version_bumps.items():
            content: str = fs.load(first_item[0], 'plain')
            version = re.search(
                first_item[1].replace(
                    '$version_pattern', r'(\d+\.\d+\.\d+(?:[ab]\d+)?)'
                ),
                content,
            ).group(1)
            break
        else:
            raise Exception
    assert version

    images = {}
    for k in ('src_max', 'src_min', 'enc_max', 'enc_min'):
        if x := data0['images'].get(k):
            if isinstance(x, str):
                images[k] = abspath(x)
            else:  # dict
                xdict: tp.Dict[str, tp.Any] = x  # noqa
                if 'start_directory' in xdict:
                    if xdict['start_directory'].startswith('..'):
                        xdict['start_directory'] = fs.normpath(
                            '{}/{}'.format(
                                fs.parent(file), xdict['start_directory']
                            )
                        )
                else:
                    xdict['start_directory'] = root
                if 'version' in xdict:
                    assert compare_version(version, '>=', xdict['version'])
                    xdict['version'] = version
                else:
                    xdict['version'] = version
                temp_file = getattr(temp_paths, k)
                version_bumps[temp_file] = '"version": "$version_pattern"'
                fs.dump(xdict, temp_file)
                images[k] = temp_file
        else:
            images[k] = None
    assert any(images.values())

    return tp.cast(
        T.Config,
        {
            'root': root,
            'version': version,
            'version_bumps': version_bumps,
            'images': images,
        },
    )


if __name__ == '__main__':
    # pox depsland/api/dev_api/build_project.py -h
    from argsense import cli

    cli.add_cmd(build)
    cli.add_cmd(bump_version_inplaces, 'bump-version')
    cli.run()
