if __name__ == '__main__':
    __package__ = 'depsland.api.dev_api'

import re
import sys
import typing as t

from lk_utils import fs
from lk_utils import run_cmd_args
from neoprint import print

from .build_offline import build as build_offline
from .build_offline_2 import build_stripped_offline
from .publish import publish as publish_to_oss
from ...paths import temp as temp_paths
from ...verspec import compare_version


class T:
    ImageKey = t.Literal['src_max', 'src_min', 'enc_max', 'enc_min']
    Path = str  # any path form
    Config = t.TypedDict(
        'Config',
        {
            'root': Path,
            'version': str,
            # the version_bumps:keys are order sensitive. the first key will be
            # treated as primary key.
            # usually the primary key indicates to "pyproject.toml" file.
            'version_bumps': t.Dict[Path, str],
            'images': t.TypedDict(
                'Images',
                {
                    'src_max': t.Union[Path, dict],
                    'src_min': t.Union[Path, dict],
                    'enc_max': t.Union[Path, dict],
                    'enc_min': t.Union[Path, dict],
                },
            ),
            'post_script': Path,  # TODO: support passing args.
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
) -> t.Tuple[str, str]:
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
            new_version = _deduce_new_version(curr_version)
        print(':r2', 'bump version: {} -> {}'.format(curr_version, new_version))
        _bump_versions(curr_version, new_version, config['version_bumps'])

    image_file = config['images'][image_key]
    assert image_file, image_key

    if publish == 1:
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

    if config['post_script']:
        run_cmd_args(
            sys.executable,
            config['post_script'],
            cwd=config['root'],
            verbose=True,
        )

    return curr_version, new_version


def bump_version(file: T.Path, new_version: str = '') -> None:
    config = load_config(file)
    curr_ver = config['version']
    new_ver = new_version or _deduce_new_version(curr_ver)
    print(':r2', 'bump version: {} -> {}'.format(curr_ver, new_ver))
    if places := config['version_bumps']:
        _bump_versions(curr_ver, new_ver, places)
    # TODO: config['version'] = new_ver


def load_config(file: T.Path, **kwargs) -> T.Config:
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
        for k, v in version_bumps.items():
            content: str = fs.load(k, 'plain')
            version = re.search(
                v.replace('$version_pattern', r'(\d+\.\d+\.\d+(?:[ab]\d+)?)'),
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
                xdict: t.Dict[str, t.Any] = x  # noqa
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

    if x := data0.get('post_script'):
        post_script = abspath(x)
    else:
        post_script = None

    return t.cast(
        T.Config,
        {
            'root': root,
            'version': version,
            'version_bumps': version_bumps,
            'images': images,
            'post_script': post_script,
        },
    )


def _bump_versions(
    old_ver: str, new_ver: str, places: t.Dict[T.Path, str]
) -> None:
    for k, v in places.items():
        content_r = fs.load(k, 'plain')
        # (a) fast but limited
        # content_w = content_r.replace(
        #     v.replace('$version_pattern', old_ver),
        #     v.replace('$version_pattern', new_ver),
        #     1
        # )
        # (b) more flexible
        content_w = re.sub(
            v.replace('$version_pattern', r'(\d+\.\d+\.\d+(?:[ab]\d+)?)'),
            v.replace('$version_pattern', new_ver),
            content_r,
            1,
        )
        assert content_w != content_r, (
            k,
            re.search(
                v.replace('$version_pattern', r'\d+\.\d+\.\d+(?:[ab]\d+)?'),
                content_r,
            ),
        )
        fs.dump(content_w, k, 'plain')


def _deduce_new_version(old: str) -> str:
    """
    example:
        0.12.0   -> 0.12.1
        0.12.1a9 -> 0.12.1a10
        0.12.1b0 -> 0.12.1b1
    """
    a, b, c, d = re.match(r'(\d+)\.(\d+)\.(\d+)([ab]\d+)?', old).groups()
    if d is None:
        return f'{a}.{b}.{int(c) + 1}'
    else:
        return f'{a}.{b}.{c}{d[0]}{int(d[1:]) + 1}'


if __name__ == '__main__':
    # pox depsland/api/dev_api/build_project.py -h
    from argsense import cli

    cli.add_cmd(build)
    cli.add_cmd(bump_version)
    cli.run()
