cd /d %~dp0
cd source
set "PYTHONUTF8=1"
..\python\python.exe -m depsland_updater request_patch
pause
