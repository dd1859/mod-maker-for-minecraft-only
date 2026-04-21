@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] Virtual environment not found.
  echo Run setup_windows.bat first.
  exit /b 1
)

if "%~1"=="" (
  set /p PROMPT=Enter mod prompt: 
) else (
  set "PROMPT=%~1"
)

if "%~2"=="" (
  set /p MODID=Enter mod id (default generatedmod): 
  if "!MODID!"=="" set "MODID=generatedmod"
) else (
  set "MODID=%~2"
)

if "%OLLAMAFREEAPI_URL%"=="" (
  if exist ".env" (
    for /f "tokens=1,* delims==" %%A in ('findstr /b /c:"OLLAMAFREEAPI_URL=" .env') do set "OLLAMAFREEAPI_URL=%%B"
  )
)

if "%OLLAMAFREEAPI_URL%"=="" (
  echo OLLAMAFREEAPI_URL is missing.
  set /p OLLAMAFREEAPI_URL=Enter OLLAMAFREEAPI_URL: 
)
if "%OLLAMAFREEAPI_KEY%"=="" set /p OLLAMAFREEAPI_KEY=Enter OLLAMAFREEAPI_KEY (can be empty): 
if "%OLLAMAFREEAPI_KEY%"=="" if not "%OPENAI_API_KEY%"=="" set "OLLAMAFREEAPI_KEY=%OPENAI_API_KEY%"
if "%OLLAMAFREEAPI_MODEL%"=="" set /p OLLAMAFREEAPI_MODEL=Enter OLLAMAFREEAPI_MODEL (default gpt-4o-mini): 
if "%OLLAMAFREEAPI_MODEL%"=="" set "OLLAMAFREEAPI_MODEL=gpt-4o-mini"

if not exist ".env" (
  (
    echo OLLAMAFREEAPI_URL=%OLLAMAFREEAPI_URL%
    echo OLLAMAFREEAPI_KEY=%OLLAMAFREEAPI_KEY%
    echo OLLAMAFREEAPI_MODEL=%OLLAMAFREEAPI_MODEL%
    echo OPENAI_API_KEY=%OLLAMAFREEAPI_KEY%
  ) > .env
)

if not exist "template\build.gradle" (
  echo [ERROR] template\build.gradle not found.
  echo Put Forge MDK files in the template folder first.
  exit /b 1
)
if not exist "template\gradlew" (
  echo [ERROR] template\gradlew not found.
  echo Put Forge MDK files in the template folder first.
  exit /b 1
)

call .venv\Scripts\activate.bat
python mod_generator.py "%PROMPT%" --mod-id "%MODID%"
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
  echo.
  echo Build failed with code %EXITCODE%.
  echo If this is your first run, double-check:
  echo  - OLLAMAFREEAPI_URL / KEY / MODEL
  echo  - template folder contains full Forge MDK
  echo  - Java 17+ is installed and on PATH
  exit /b %EXITCODE%
)

echo Done.
exit /b 0
