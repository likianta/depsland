@REM put depsland in "dist\depsland"
cd %~dp0
depsland\setup.exe
set DEPSLAND=%~dp0depsland\src
depsland\src\depsland.bat build\setup.py
pause