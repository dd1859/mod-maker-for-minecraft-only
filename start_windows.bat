@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] .venv not found. Run setup_windows.bat first.
  exit /b 1
)

if "%~1"=="" (
  set /p PROMPT=Enter mod prompt: 
) else (
  set "PROMPT=%~1"
)

if "%~2"=="" (
  set /p MODID=Enter mod id ^(default generatedmod^): 
  if "!MODID!"=="" set "MODID=generatedmod"
) else (
  set "MODID=%~2"
)

if "%OPENAI_API_KEY%"=="" if "%OLLAMAFREEAPI_KEY%"=="" (
  set /p OPENAI_API_KEY=Enter OPENAI_API_KEY: 
)
if "%OPENAI_API_URL%"=="" if "%OLLAMAFREEAPI_URL%"=="" (
  set /p OPENAI_API_URL=Enter OPENAI_API_URL ^(default https://api.openai.com/v1/chat/completions^): 
  if "!OPENAI_API_URL!"=="" set "OPENAI_API_URL=https://api.openai.com/v1/chat/completions"
)
if "%OPENAI_MODEL%"=="" if "%OLLAMAFREEAPI_MODEL%"=="" set "OPENAI_MODEL=gpt-4o-mini"

if not exist "template\build.gradle" (
  echo [ERROR] template\build.gradle missing.
  exit /b 1
)
if not exist "template\gradlew" (
  echo [ERROR] template\gradlew missing.
  exit /b 1
)

if not exist ".env" (
  (
    echo OPENAI_API_KEY=%OPENAI_API_KEY%
    echo OPENAI_API_URL=%OPENAI_API_URL%
    echo OPENAI_MODEL=%OPENAI_MODEL%
  ) > .env
)

call .venv\Scripts\activate.bat
python mod_generator.py "%PROMPT%" --mod-id "%MODID%"
set "RC=%ERRORLEVEL%"
if not "%RC%"=="0" (
  echo Build failed with code %RC%.
  exit /b %RC%
)

echo Done.
exit /b 0
