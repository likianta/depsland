import typing as tp

import neoprint as np
import streamlit_canary as sc

# @sc.init_state
# class State:
#     depsland_zip: str = ''
#     old_pypi_path: str = ''



def main() -> tp.Tuple[str, str]:
    depsland_zip = sc.path_input(
        'Input path to "depsland.7z"',
        help='If you have downloaded Depsland package, input path here.',
    )
    if depsland_zip:
        assert depsland_zip.endswith(('.7z', '.zip'))
    
    old_pypi_path = sc.path_input(
        'Input path to "pypi" folder',
        help='If you have installed Depsland before, input its "pypi" folder '
        'path here (absolute path).',
    )
    if old_pypi_path:
        assert old_pypi_path.endswith('/pypi')
    
    np.show(depsland_zip, old_pypi_path, ':n')
    return depsland_zip, old_pypi_path
