cd /d %~dp0
set PYTHONPATH=.;chore/site_packages
.\python\python.exe -m depsland launch-gui
pause
