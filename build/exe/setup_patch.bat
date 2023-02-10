@echo off
cd /d %~dp0
.\python\python.exe -B build/depsland_setup.py --not-do-replace-site-packages
