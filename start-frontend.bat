@echo off
setlocal
echo ====================================
echo   Starting Velora AI Frontend
echo ====================================
echo.

set "ROOT_DIR=%~dp0"
set "FRONTEND_DIR=%ROOT_DIR%frontend"

if not exist "%FRONTEND_DIR%\package.json" (
    echo Frontend directory not found: "%FRONTEND_DIR%"
    exit /b 1
)

where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo npm not found. Install Node.js LTS and retry.
    exit /b 1
)

cd /d "%FRONTEND_DIR%"

if not exist node_modules (
    echo Installing dependencies...
    npm install
    echo.
)

echo ====================================
echo   Starting Vite Dev Server
echo ====================================
echo Frontend will run at: http://localhost:5173
echo Press Ctrl+C to stop
echo.

npm run dev -- --host 0.0.0.0 --port 5173
