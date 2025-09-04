@echo off
cd /d %~dp0
set "PYTHONBREAKPOINT=0"
set "PYTHONUTF8=1"
.\python\python.exe -m depsland launch-gui
