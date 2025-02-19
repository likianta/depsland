@echo off
set "PYTHONBREAKPOINT=0"
set "PYTHONPATH=%DEPSLAND%"
set "PYTHONUTF8=1"
"%DEPSLAND%\python\python.exe" -m depsland %*
