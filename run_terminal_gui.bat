@echo off
REM Set working directory to the script's location
cd /d %~dp0

echo Checking for Python installation...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python and ensure it is added to PATH.
    pause
    exit /b
)

echo Checking for requirements.txt...

REM If requirements.txt doesn't exist, generate it using requirement_scanner.py
if not exist requirements.txt (
    echo Generating requirements.txt...
    if exist requirement_scanner.py (
        python requirement_scanner.py
    ) else (
        echo ERROR: requirement_scanner.py not found. Please check the script.
        pause
        exit /b
    )
)

echo Installing required dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Fix scikit-learn issue by ensuring it's installed correctly
pip uninstall -y sklearn
pip install scikit-learn

echo Running requirement scanner...
if exist requirement_scanner.py (
    python requirement_scanner.py
) else (
    echo WARNING: requirement_scanner.py not found. Skipping requirement scanning.
)

echo Starting Terminal UI...
if exist terminal_ui.py (
    python terminal_ui.py
) else (
    echo ERROR: terminal_ui.py not found. Please check the script.
    pause
    exit /b
)

pause
