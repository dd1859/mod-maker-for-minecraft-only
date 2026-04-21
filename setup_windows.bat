@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

where curl >nul 2>&1
if errorlevel 1 (
  echo [ERROR] curl was not found on PATH.
  exit /b 1
)

echo === Checking Python ===
where python >nul 2>&1
if errorlevel 1 (
  echo Installing Python 3.12...
  set "PY_EXE=%TEMP%\python-installer.exe"
  curl -L "https://www.python.org/ftp/python/3.12.9/python-3.12.9-amd64.exe" -o "%PY_EXE%"
  if errorlevel 1 exit /b 1
  "%PY_EXE%" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
)
where python >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python still missing on PATH. Restart terminal and try again.
  exit /b 1
)

echo === Checking Java (JDK 17+) ===
set "JAVA_OK=0"
where java >nul 2>&1
if not errorlevel 1 (
  for /f "tokens=3" %%v in ('java -version 2^>^&1 ^| findstr /i "version"') do set "JAVA_VERSION_RAW=%%v"
  set "JAVA_VERSION_RAW=!JAVA_VERSION_RAW:\="
  for /f "tokens=1 delims=." %%m in ("!JAVA_VERSION_RAW!") do set "JAVA_MAJOR=%%m"
  if not "!JAVA_MAJOR!"=="" if !JAVA_MAJOR! GEQ 17 set "JAVA_OK=1"
)
if "!JAVA_OK!"=="0" (
  echo Installing Temurin JDK 17...
  set "JDK_MSI=%TEMP%\temurin-jdk17.msi"
  curl -L "https://github.com/adoptium/temurin17-binaries/releases/latest/download/OpenJDK17U-jdk_x64_windows_hotspot_latest.msi" -o "%JDK_MSI%"
  if errorlevel 1 exit /b 1
  msiexec /i "%JDK_MSI%" /qn /norestart
)

where java >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Java still missing on PATH. Restart terminal and try again.
  exit /b 1
)

echo === Creating virtual environment ===
python -m venv .venv
if errorlevel 1 exit /b 1
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if exist requirements.txt pip install -r requirements.txt

echo Setup complete.
echo Next: run start_windows.bat
exit /b 0
