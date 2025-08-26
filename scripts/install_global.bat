@echo off
setlocal

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Create the global command script
set GLOBAL_SCRIPT=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\agent.bat

echo @echo off > "%GLOBAL_SCRIPT%"
echo python "%SCRIPT_DIR%agent_cli.py" %%* >> "%GLOBAL_SCRIPT%"

echo.
echo ✅ Global agent command installed successfully!
echo.
echo You can now use your agent globally with:
echo   agent "Your query here"
echo   agent -i
echo.
echo The command is available from anywhere in your system.
echo.

REM Test the installation
echo Testing the installation...
call agent --version

if %errorlevel% equ 0 (
    echo.
    echo ✅ Installation test successful!
) else (
    echo.
    echo ❌ Installation test failed. Please check the setup.
)

echo.
pause