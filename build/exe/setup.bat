@echo off
cd /d %~dp0
set PYTHONPATH=.;build;chore/site_packages
.\python\python.exe -m setup_wizard
