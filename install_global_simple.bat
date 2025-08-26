@echo off
setlocal

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Create the global command script
set GLOBAL_SCRIPT=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\agent.bat

echo @echo off > "%GLOBAL_SCRIPT%"
echo python "%SCRIPT_DIR%src\ollama_agent\cli\main.py" %%* >> "%GLOBAL_SCRIPT%"

echo.
echo ✅ Global agent command updated for new project structure!
echo.
echo You can now use your agent globally with:
echo   agent "Your query here"
echo   agent -i
echo.
echo The command now uses the restructured package in src/ollama_agent/cli/
echo.

REM Test the installation
echo Testing the installation...
call agent --version

if %errorlevel% equ 0 (
    echo.
    echo ✅ Installation test successful!
) else (
    echo.
    echo ❌ Installation test failed. You may need to install the package first with:
    echo    pip install -e .
)

echo.
pause