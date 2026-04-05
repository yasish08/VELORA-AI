@echo off
setlocal
echo ====================================
echo   Starting Velora AI Backend
echo ====================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"

if not exist "%BACKEND_DIR%\main.py" (
    echo Backend directory not found: "%BACKEND_DIR%"
    exit /b 1
)

where py >nul 2>nul
if %errorlevel%==0 (
    set "PY_CMD=py -3"
) else (
    where python >nul 2>nul
    if %errorlevel% neq 0 (
        echo Python not found. Install Python 3.10+ and retry.
        exit /b 1
    )
    set "PY_CMD=python"
)

cd /d "%BACKEND_DIR%"

if not exist venv (
    echo Creating virtual environment...
    %PY_CMD% -m venv venv
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo ====================================
echo   Starting FastAPI Server
echo ====================================
echo Backend will run at: http://127.0.0.1:8000
echo Press Ctrl+C to stop
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
