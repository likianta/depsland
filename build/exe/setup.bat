@echo off
cd /d %~dp0
set PYTHONPATH=.
.\python\python.exe -B build/setup_wizard/run.py
