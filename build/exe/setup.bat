@echo off
cd /d %~dp0
set PYTHONPATH=.
.\python\python.exe build/setup_wizard/run.py
