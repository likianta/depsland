from argsense import cli
from lk_utils import fs
from lk_utils import xpath


@cli.cmd()
def clean_up_temp_dir():
    for d in fs.find_dirs(xpath('../temp')):
        if d.name not in (
                'unittests',
        ):
            print(':ir', f'[red dim]delete {d.name}[/]')
            fs.remove_tree(d.path)


if __name__ == '__main__':
    cli.run()
