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

from .patch_client import patch_online
