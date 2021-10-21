cd %~dp0
depsland\venv\python.exe -B depsland\build\doctor.py
depsland\venv\python.exe -B depsland\src\pylauncher.py
depsland\src\depsland.bat build\setup.py
pause