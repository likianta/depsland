from lk_utils import dump
from lk_utils.textwrap import dedent

from ...manifest import T


def make_shell(manifest: T.Manifest, file_o: str) -> str:
    assert file_o.endswith('.sh')
    # template = dedent('''
    #     # cd to current dir
    #     # https://stackoverflow.com/a/246128
    #     CURR_DIR=$( cd -- "$( dirname -- "${{BASH_SOURCE[0]}}" )" &> \\
    #     /dev/null && pwd )
    #     cd $CURR_DIR/source
    #
    #     export PYTHONPATH=.
    #     python/bin/python3 -m depsland run {appid} --version {version}
    # ''', join_sep='\\')
    template = dedent('''
        #!source/python/bin/python3
        
        import os
        import subprocess as sp
        import sys
        # from pprint import pprint
        
        # pprint(sys.argv)
        curr_file = sys.argv[0]
        curr_dir = os.path.dirname(curr_file)
        os.chdir(f'{{curr_dir}}/source')
        # pprint(os.getcwd())
        
        os.environ['PYTHONPATH'] = '.'
        sp.run((
            sys.executable, '-m', 'depsland',
            'run', '{appid}',
            *sys.argv[1:]
        ))
    ''')
    script = template.format(
        appid=manifest['appid'],
        version=manifest['version'],
    )
    dump(script, file_o)
    return file_o
