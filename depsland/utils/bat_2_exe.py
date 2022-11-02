import os.path
from pathlib import Path

from lk_utils import loads


def bat_2_exe(file_i: str, file_o: str = '',
              icon: str = '', show_console=True) -> str:
    """
    args:
        file_i: a ".bat" file.
    
    kwargs:
        file_o: a ".exe" file.
        icon: a ".ico" file. ([red dim]it must be .ico[/])
    """
    assert file_i.endswith('.bat')
    if file_o:
        assert file_o.endswith('.exe')
    else:
        file_o = file_i.removesuffix('.bat') + '.exe'
    if icon:
        icon = os.path.abspath(icon)
    
    data_r: list[str] = loads(file_i).splitlines()
    data_w = ' && '.join(data_r).strip()
    
    # https://github.com/silvandeleemput/gen-exe
    # https://blog.csdn.net/qq981378640/article/details/52980741
    data_w = data_w.replace('%~dp0', '{EXE_DIR}').replace('%cd%', '{EXE_DIR}')
    if data_w.endswith('%*'): data_w = data_w[:-3]
    
    # pip install gen-exe  # this is only available for windows
    from genexe.generate_exe import generate_exe  # noqa
    generate_exe(
        target=Path(file_o),
        command=data_w,
        icon_file=Path(icon) if icon else None,
        show_console=show_console
    )
    
    return file_o