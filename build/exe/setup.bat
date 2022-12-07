@echo off
cd /d %~dp0
set PYTHONPATH=.
.\python\pythonw.exe -B build/setup_wizard/main.py :false :false
