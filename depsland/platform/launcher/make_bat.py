"""
for windows only.
"""
from lk_utils import dump
from lk_utils.textwrap import dedent

from ...manifest import T


def make_bat(
    manifest: T.Manifest,
    file_o: str,
    *,
    debug: bool = False,
    custom_cd: '' = None,  # TEST
) -> str:
    assert file_o.endswith('.bat')
    # if debug:
    #     template = dedent(r'''
    #         cd /d %~dp0
    #         cd source
    #         set PYTHONPATH=.;chore/site_packages
    #         .\python\python.exe -m depsland run {appid}
    #         pause
    #     ''')
    # else:
    #     template = dedent(r'''
    #         @echo off
    #         cd /d %~dp0
    #         cd source
    #         set PYTHONPATH=.;chore/site_packages
    #         .\python\python.exe -m depsland run {appid}
    #     ''')
    # script = template.format(
    #     appid=manifest['appid'],
    #     version=manifest['version'],
    # )
    script = dedent(
        r'''
        {echo_off}
        cd /d %~dp0
        {cd}
        set "PYTHONPATH=.;chore/site_packages"
        set "PYTHONUTF8=1"
        .\python\python.exe -m depsland run {appid}
        {pause}
        '''.format(
            echo_off='' if debug else '@echo off',
            cd=custom_cd or 'cd ../../../',
            appid=manifest['appid'],
            pause='pause' if debug else '',
        )
    )
    dump(script, file_o)
    return file_o
