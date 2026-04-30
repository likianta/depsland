if 1:
    import lk_logger
    from argsense import cli
    from lk_utils import fs

    lk_logger.unload()
if 2:
    from objprint import op


@cli
def inspect_snapdep(snap_id: str) -> None:
    file = f'pypi/index/snapdep/{snap_id}.pkl'
    data = fs.load(file)
    op(tuple('{}. {}'.format(i, v['id']) for i, v in enumerate(data.values())))


if __name__ == '__main__':
    cli.run()
