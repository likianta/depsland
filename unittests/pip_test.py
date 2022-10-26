from argsense import cli
from depsland import paths
from depsland import pip


@cli.cmd()
def is_pip_shown_its_message_on_stdout():
    pip.test()


@cli.cmd()
def show_pip_version():
    print(pip.pip_version())


@cli.cmd()
def download_test(package='lambda-ex'):
    pip.download(package, dest=paths.Temp.unittests)


if __name__ == '__main__':
    cli.run()
