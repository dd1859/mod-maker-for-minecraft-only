@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM AI Minecraft Mod Generator - Windows setup
REM This script checks dependencies and installs missing ones using curl-downloaded installers.

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

where curl >nul 2>&1
if errorlevel 1 (
  echo [ERROR] curl is required but was not found on PATH.
  echo Please install curl (or update Windows) and re-run this script.
  exit /b 1
)

echo.
echo === Checking Python ===
where python >nul 2>&1
if errorlevel 1 (
  echo Python not found. Downloading Python installer...
  set "PY_EXE=%TEMP%\python-installer.exe"
  curl -L "https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe" -o "%PY_EXE%"
  if errorlevel 1 (
    echo [ERROR] Failed downloading Python installer.
    exit /b 1
  )
  echo Installing Python silently...
  "%PY_EXE%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
  if errorlevel 1 (
    echo [ERROR] Python installer failed.
    exit /b 1
  )
  echo Python installed.
) else (
  for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo Found %%i
)

echo.
echo === Checking Java (JDK 17+) ===
where java >nul 2>&1
if errorlevel 1 (
  echo Java not found. Downloading Temurin JDK 17 MSI...
  set "JDK_MSI=%TEMP%\temurin-jdk17.msi"
  curl -L "https://github.com/adoptium/temurin17-binaries/releases/latest/download/OpenJDK17U-jdk_x64_windows_hotspot_latest.msi" -o "%JDK_MSI%"
  if errorlevel 1 (
    echo [ERROR] Failed downloading JDK installer.
    exit /b 1
  )
  echo Installing JDK silently...
  msiexec /i "%JDK_MSI%" /qn /norestart
  if errorlevel 1 (
    echo [ERROR] JDK install failed.
    exit /b 1
  )
  echo JDK installed.
) else (
  java -version
)

echo.
echo === Creating venv and installing Python deps ===
python -m venv .venv
if errorlevel 1 (
  echo [ERROR] Failed creating virtual environment.
  exit /b 1
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
  echo [ERROR] Failed activating virtual environment.
  exit /b 1
)

python -m pip install --upgrade pip
if exist requirements.txt (
  pip install -r requirements.txt
  if errorlevel 1 (
    echo [ERROR] pip install failed.
    exit /b 1
  )
)

echo.
echo === Setup complete ===
echo Next steps:
echo   1) set OLLAMAFREEAPI_URL, OLLAMAFREEAPI_KEY, OLLAMAFREEAPI_MODEL
echo   2) run start_windows.bat
exit /b 0
