from lk_utils import dumps
from lk_utils import fs


def init_pypi(target_dir: str = fs.xpath('../chore/pypi_clean')) -> None:
    fs.make_dir(f'{target_dir}/cache')
    fs.make_dir(f'{target_dir}/downloads')
    fs.make_dir(f'{target_dir}/index')
    fs.make_dir(f'{target_dir}/installed')

    dumps({}, f'{target_dir}/index/dependencies.pkl')
    dumps({}, f'{target_dir}/index/name_2_versions.pkl')
    dumps({}, f'{target_dir}/index/name_id_2_paths.pkl')
    dumps({}, f'{target_dir}/index/updates.pkl')


if __name__ == '__main__':
    # py sidework/pypi_init.py
    init_pypi()
