cd /d %~dp0
set PYTHONPATH=%DEPSLAND%
"%DEPSLAND%\python\python.exe" -m depsland launch-gui
