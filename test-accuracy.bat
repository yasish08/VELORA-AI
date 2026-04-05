@echo off
REM Velora AI - Prediction Accuracy Test Runner
REM Runs quick accuracy validation

echo.
echo ========================================
echo   VELORA AI - ACCURACY TEST
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found.
    echo Please run setup first.
    pause
    exit /b 1
)

echo Running quick accuracy test...
echo.

venv\Scripts\python.exe quick_test.py

echo.
echo ========================================
echo.
echo To run full test suite, execute:
echo   cd backend
echo   venv\Scripts\python.exe tests\test_accuracy.py
echo.
echo ========================================
pause
