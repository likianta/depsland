import ctypes
import os
if os.name == 'nt':
    import winreg


def check_if_long_path_limit_unlocked():
    dll = ctypes.WinDLL('ntdll')
    if hasattr(dll, 'RtlAreLongPathsEnabled'):
        dll.RtlAreLongPathsEnabled.restype = ctypes.c_ubyte
        dll.RtlAreLongPathsEnabled.argtypes = ()
        return bool(dll.RtlAreLongPathsEnabled())
    else:
        return False
