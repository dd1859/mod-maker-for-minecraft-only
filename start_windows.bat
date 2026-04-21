@echo off
setlocal EnableExtensions

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment not found.
  echo Run setup_windows.bat first.
  exit /b 1
)

if "%~1"=="" (
  echo Usage:
  echo   start_windows.bat "your mod prompt" [mod_id]
  exit /b 1
)

set "PROMPT=%~1"
set "MODID=%~2"
if "%MODID%"=="" set "MODID=generatedmod"

if "%OLLAMAFREEAPI_URL%"=="" (
  echo [ERROR] OLLAMAFREEAPI_URL is not set.
  echo Example:
  echo   set OLLAMAFREEAPI_URL=https://your-endpoint/v1/chat/completions
  exit /b 1
)

call .venv\Scripts\activate.bat
python mod_generator.py "%PROMPT%" --mod-id "%MODID%"
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
  echo Build failed. Exit code: %EXITCODE%
  exit /b %EXITCODE%
)

echo Done.
exit /b 0
