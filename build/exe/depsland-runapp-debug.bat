cd /d "%DEPSLAND%"
set "PYTHONPATH=.;chore/site_packages"
set "PYTHONUTF8=1"
.\python\python.exe -m depsland run --caller-location %0
pause
