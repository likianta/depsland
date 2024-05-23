from argsense import cli


@cli.cmd()
def hello(name: str = 'world') -> None:
    print(f'hello {name}!')


if __name__ == '__main__':
    cli.run()
