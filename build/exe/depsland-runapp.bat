@echo off
cd /d %~dp0
cd ../../../
set "PYTHONBREAKPOINT=0"
set "PYTHONUTF8=1"
.\python\python.exe -m depsland run --caller-location %0
