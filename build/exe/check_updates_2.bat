REM https://chatgpt.com/share/6ab1fd38-a9b0-83ee-8daa-335d3b4e4b69
@echo off
cd /d %~dp0
cd source
set "NEOPRINT_LEGACY_WINDOWS=1"
set "PYTHONUTF8=1"
@echo on
..\python\python.exe -m depsland_updater request_patch
@if errorlevel 1 pause
