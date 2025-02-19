cd /d %~dp0
set "PYTHONBREAKPOINT=0"
set "PYTHONPATH=.;chore/site_packages"
set "PYTHONUTF8=1"
.\python\python.exe -m depsland launch-gui
pause
