from argsense import cli


@cli.cmd()
def main(name: str):
    print(f'hello, {name}!')


if __name__ == '__main__':
    cli.run(main)
