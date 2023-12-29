from lk_utils import dumps
from lk_utils.textwrap import dedent

from ...manifest import T


def make_shell(manifest: T.Manifest, file_o: str) -> str:
    assert file_o.endswith('.sh')
    template = dedent('''
        # cd to current dir
        # https://stackoverflow.com/a/246128
        CURR_DIR=$( cd -- "$( dirname -- "${{BASH_SOURCE[0]}}" )" &> \\
        /dev/null && pwd )
        cd $CURR_DIR/source
        
        export PYTHONPATH=.
        python/bin/python3 -m depsland run {appid} --version {version}
    ''', join_sep='\\')
    script = template.format(
        appid=manifest['appid'],
        version=manifest['version'],
    )
    dumps(script, file_o)
    return file_o
