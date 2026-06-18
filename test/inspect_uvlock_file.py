from argsense import cli
from lk_utils import fs
from neoprint import print


@cli
def main(file: str = 'uv.lock'):
    data = fs.load(file, 'toml')

    possible_keys_for_dep = set()

    for item in data['package']:
        for dep in item.get('dependencies', ()):
            try:
                assert 'name' in dep
                # assert len(dep) == 1
            except AssertionError as e:
                e.add_note(str({'item': item['name'], 'dep': dep}))
                raise e

            possible_keys_for_dep.update(dep.keys())

    print(sorted(possible_keys_for_dep), ':l')


cli.run(main)
