"""
Usage:
    # silent update
    # in your main script...

    ...
    import depsland_updater
    from lk_utils import run_new_thread
    
    ...
    run_new_thread(depsland_updater.patch_online)
"""

from .direct_request import apply_patch_from_local
from .direct_request import get_project_dir
from .direct_request import request_patch
from .proxy_service import patch_online
