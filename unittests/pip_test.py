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
def test_download(test_package='lambda-ex'):
    pip.download(test_package, dest=paths.Temp.unittests)


@cli.cmd()
def test_install(test_package='lambda-ex'):
    pip.install(test_package, dest=paths.Temp.unittests)
    print('see result in {}/{}'.format(
        paths.Temp.unittests, test_package.replace('-', '_')
    ))


if __name__ == '__main__':
    cli.run()
