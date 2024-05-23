from argsense import cli
from depsland.manifest import load_manifest


@cli.cmd('view')
def view_manifest(file: str) -> None:
    m = load_manifest(file)
    print(m.model, ':l')


if __name__ == '__main__':
    # pox sidework/manifest_viewer.py view -h
    # pox sidework/manifest_viewer.py view oss/apps/hello_world/manifest.pkl
    cli.run()
