if __name__ == '__main__':
    __package__ = 'depsland.api.dev_api'
    
import os
import re
import tree_shaking
import typing as t
from lk_utils import fs
from lk_utils import timestamp
from pyportable_crypto import compile_dir
from pyportable_crypto.cipher_gen import generate_cipher_package


class T:
    Path = str
    Config = t.TypedDict('Config', {
        'root': Path,
        'version_bump': t.TypedDict('VersionBump', {
            'places': t.Dict[Path, str],
        }),
        'images': t.TypedDict('Images', {
            'source-mini': Path,
            'source-full': Path,
            'encrypted-mini': Path,
            'encrypted-full': Path,
        }),
        'encryption_options': t.TypedDict('EncryptionOptions', {
            'key': str,  # a string or `<ENV>` or `<ENV:VARNAME>`
            'packages': t.List[Path],
            'output': Path,
        }),
        'minideps_options': t.TypedDict('MinidepsOptions', {
            'tree_shaking_model': Path,
            'output': Path,
        }),
        'post_script': Path,
    })


def build(
    file: T.Path,
    new_version: str = None,
    minify_deps: int = 0,
    encrypt_packages: int = 0,
    secret_key: str = None,
    publish: int = 0,
    remain_last_version: bool = False,
) -> t.Tuple[str, str]:
    """
    params:
        new_version (-v):
        minify_deps (-m):
            0: do not minimize.
            1: enable minimize mode, but use existing results.
            2: enable minimize mode, and re-generate the results.
        encrypt_packages (-e):
            0: do not encrypt.
            1: enable encryption, but use existing results.
            2: enable encryption, and re-generate the results.
                you must set `secret_key` in this case.
        secret_key (-s): required if `encrypt_packages==2`.
            caution: do not frequently change the secret key, because -
            recompiling a new key is time-consuming.
        publish (-p):
            0: do not publish.
            1: generate a standalone package, you can manually publish it, or -
            share it with others by local area network.
            2: generate a standalone package, and publish it via depsland -
            official server.
            tip: if you set `minify_deps` other than 0, we recommend setting -
            this option 1 or 0.
    """
    config = _load_config(file, secret_key=secret_key)
    
    curr_version = _get_current_version(config)
    if remain_last_version:
        print(':sv6', 'use last time updated version', curr_version)
        new_version = curr_version
    else:
        if new_version is None:
            new_version = _deduce_new_version(curr_version)
        print(':r2', 'bump version: {} -> {}'.format(curr_version, new_version))
        _bump_versions(
            curr_version, new_version, config['version_bump']['places']
        )
    
    # noinspection PyTypedDict
    image_file = config['images']['{}-{}'.format(
        'encrypted' if encrypt_packages else 'source',
        'full' if minify_deps else 'mini',
    )]
    assert image_file
    
    if minify_deps == 2:
        assert all(config['minideps_options'].values())
        model = config['minideps_options']['tree_shaking_model']
        tree_shaking.build_module_graphs(model)
        tree_shaking.dump_tree(model, config['minideps_options']['output'])
    
    if encrypt_packages:
        assert all(config['encryption_options'].values())
        enc = config['encryption_options']
        if encrypt_packages == 1:
            print('use last time encrypted packages')
            _patch_encrypted_packages(
                enc['packages'],
                enc['output'],
                tuple(config['version_bump']['places'].keys())
            )
        else:
            _encrypt_packages(enc['packages'], enc['output'], enc['key'])
    
    if publish == 1:
        import depsland.api
        # from ..build_offline import main as build_offline
        depsland.api.build_offline(image_file)
    elif publish == 2:
        import depsland.api
        # from ..publish import main as publish
        depsland.api.publish(image_file, upload_dependencies=True)

    if config['post_script']:
        exec(fs.load(config['post_script'], 'plain'))
    
    return curr_version, new_version


def bump_version(file: T.Path, new_version: str = None) -> None:
    config = _load_config(file)
    curr_ver = _get_current_version(config)
    new_ver = new_version or _deduce_new_version(curr_ver)
    print(':r2', 'bump version: {} -> {}'.format(curr_ver, new_ver))
    _bump_versions(curr_ver, new_ver, config['version_bump']['places'])


def _bump_versions(
    old_ver: str, new_ver: str, places: t.Dict[T.Path, str]
) -> None:
    for k, v in places.items():
        content_r = fs.load(k, 'plain')
        content_w = content_r.replace(
            v.replace('<VERSION>', old_ver),
            v.replace('<VERSION>', new_ver),
            1
        )
        assert content_w != content_r
        # content_w = re.sub(
        #     v, lambda m: m.group(0).replace(m.group(1), new_ver), content
        # )
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


def _encrypt_packages(
    targets: t.Iterable[str], output_root: str, key: str
) -> None:
    fs.copy_tree(
        generate_cipher_package(key),
        '{}/pyportable_runtime'.format(output_root),
        True,
    )
    for t in targets:
        dir_i = t
        dir_o = '{}/{}'.format(output_root, fs.basename(t))
        compile_dir(dir_i, dir_o, key, add_runtime_package='none')


def _get_current_version(config: T.Config) -> str:
    for k, v in config['version_bump']['places'].items():
        content: str = fs.load(k, 'plain')
        return re.search(
            v.replace('<VERSION>', r'(\d+\.\d+\.\d+(?:[ab]\d+)?)'),
            content
        ).group(1)
    else:
        raise Exception


def _load_config(file: T.Path, **kwargs) -> T.Config:
    data0: T.Config = fs.load(file)
    
    root = fs.normpath('{}/{}'.format(fs.parent(file), data0['root']))
    
    def abspath(x: str) -> T.Path:
        assert x
        return '{}/{}'.format(root, x)
    
    places = {}
    for k, v in data0['version_bump']['places'].items():
        places[abspath(k)] = v
    assert places
    
    images = {}
    for k in ('source-mini', 'source-full', 'encrypted-mini', 'encrypted-full'):
        # noinspection PyTypedDict
        if x := data0['images'].get(k):
            # noinspection PyTypeChecker
            images[k] = abspath(x)
        else:
            images[k] = None
    assert any(images.values())
    
    encryption_key = ''
    encryption_dirs = []
    encryption_output = ''
    if x := data0.get('encryption_options'):
        if kwargs.get('secret_key'):
            encryption_key = kwargs['secret_key']
        elif x['key']:
            if x['key'] == '<ENV>':
                encryption_key = os.environ['DEPSLAND_ENCRYPTION_KEY']
            elif x['key'].startswith('<ENV:'):
                encryption_key = os.environ[x['key'][5:-1]]
            else:
                encryption_key = x['key']
        for d in x['packages']:
            encryption_dirs.append(abspath(d))
        if x['output']:
            encryption_output = abspath(x['output'])
    
    tree_shaking_model = ''
    tree_shaking_output = ''
    if x := data0.get('minideps_options'):
        tree_shaking_model = abspath(x['tree_shaking_model'])
        if y := x.get('output'):
            tree_shaking_output = abspath(y)
        else:
            tree_shaking_output = 'temp/tree_shaking_results/{}'.format(
                timestamp('ymd-hns')
            )
    
    if x := data0.get('post_script'):
        post_script = abspath(x)
    else:
        post_script = None
    
    return {
        'root': root,
        'version_bump': {
            'places': places,
        },
        'images': images,  # noqa
        'encryption_options': {
            'key': encryption_key,
            'packages': encryption_dirs,
            'output': encryption_output,
        },
        'minideps_options': {
            'tree_shaking_model': tree_shaking_model,
            'output': tree_shaking_output,
        },
        'post_script': post_script,
    }


def _patch_encrypted_packages(
    packages: t.Iterable[str],
    output_root: T.Path,
    version_changed_files: t.Iterable[str]
) -> None:
    for dir in packages:
        for file in version_changed_files:
            if file.startswith(dir + '/'):
                file_i = file
                file_o = '{}/{}'.format(
                    output_root, fs.relpath(file, fs.parent(dir))
                )
                print(
                    'fast encrypt to version changed file: {} -> {}'
                    .format(file_i, file_o)
                )
                fs.copy_file(file_i, file_o, True)


if __name__ == '__main__':
    # pox depsland/api/dev_api/build_project.py -h
    from argsense import cli
    cli.add_cmd(build)
    cli.add_cmd(bump_version)
    cli.run()
