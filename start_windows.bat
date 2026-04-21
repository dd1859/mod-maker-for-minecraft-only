@echo off
setlocal EnableExtensions

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv not found. Run setup_windows.bat first.
  exit /b 1
)

call .venv\Scripts\activate.bat
python mod_generator.py
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo UI exited with code %RC%.
  exit /b %RC%
)

exit /b 0
