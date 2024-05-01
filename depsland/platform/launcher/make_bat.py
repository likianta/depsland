"""
for windows only.
"""
from lk_utils import dumps
from lk_utils.textwrap import dedent

from ...manifest import T


def make_bat(manifest: T.Manifest, file_o: str, *, debug: bool = False) -> str:
    assert file_o.endswith('.bat')
    if debug:
        template = dedent(r'''
            cd /d %~dp0
            cd source
            set PYTHONPATH=.;chore/site_packages
            .\python\python.exe -m depsland run {appid}
            pause
        ''')
    else:
        template = dedent(r'''
            @echo off
            cd /d %~dp0
            cd source
            set PYTHONPATH=.;chore/site_packages
            .\python\python.exe -m depsland run {appid}
        ''')
    script = template.format(
        appid=manifest['appid'],
        version=manifest['version'],
    )
    dumps(script, file_o)
    return file_o
