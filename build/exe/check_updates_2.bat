cd /d %~dp0
cd source
set "NEOPRINT_LEGACY_WINDOWS=1"
set "PYTHONUTF8=1"
..\python\python.exe -m depsland_updater request_patch
pause
