@echo off
cd /d %~dp0
cd ../../../
set "PYTHONBREAKPOINT=0"
set "PYTHONPATH=.;lib;.venv"
set "PYTHONUTF8=1"
@REM .\python\python.exe -m depsland run --caller-location %0 %*
.\python\python.exe depsland/__main__.py run --caller-location %0 %*
