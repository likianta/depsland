cd /d %~dp0
cd ../../../
set "PYTHONBREAKPOINT=0"
set "PYTHONPATH=.;lib;.venv"
set "PYTHONUTF8=1"
.\python\python.exe depsland/__main__.py run --caller-location %0 %*
pause
