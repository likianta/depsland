@echo off
set PYTHONPATH=%DEPSLAND%
set PYTHONUTF8=1
"%DEPSLAND%\python\python.exe" -m depsland %*
