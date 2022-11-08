@echo off
cd /d %~dp0
$DEPSLAND$\python\python.exe -B build/depsland_setup.py --not-do-replace-site-packages
