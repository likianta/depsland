from platform import system

CURRENT_OS = system().lower()

IS_LINUX = CURRENT_OS == 'linux'
IS_MACOS = CURRENT_OS == 'darwin'
IS_WINDOWS = CURRENT_OS == 'windows'
