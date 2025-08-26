@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting MCP Agent System...
echo.

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

REM Check if Python is available
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.13+ and add it to your PATH
    pause
    exit /b 1
)
echo ✅ Python is available

REM Check if Ollama is running
echo 🔍 Checking Ollama service...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Ollama is not running. Starting Ollama...
    start "" "ollama" "serve"
    echo ⏳ Waiting for Ollama to start...
    timeout /t 5 /nobreak >nul
    
    REM Check again
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo ❌ Failed to start Ollama. Please start it manually with 'ollama serve'
        pause
        exit /b 1
    )
)
echo ✅ Ollama is running

REM Check if required models are available
echo 🔍 Checking AI models...
ollama list | findstr "gemma3:12b" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Model gemma3:12b not found. Pulling model...
    echo This may take a while...
    ollama pull gemma3:12b
    if %errorlevel% neq 0 (
        echo ❌ Failed to pull gemma3:12b model
        pause
        exit /b 1
    )
)

ollama list | findstr "gemma3:1b" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Model gemma3:1b not found. Pulling model...
    ollama pull gemma3:1b
    if %errorlevel% neq 0 (
        echo ❌ Failed to pull gemma3:1b model
        pause
        exit /b 1
    )
)
echo ✅ AI models are available

REM Check if dependencies are installed
echo 🔍 Checking Python dependencies...

REM Check if virtual environment exists, create if not
if not exist "%SCRIPT_DIR%\.venv" (
    echo ⚠️ Virtual environment not found. Creating .venv...
    python -m venv "%SCRIPT_DIR%\.venv"
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

REM Activate virtual environment and install dependencies
echo 🔧 Activating virtual environment and checking dependencies...
call "%SCRIPT_DIR%\.venv\Scripts\activate.bat"
python -c "import mcp; import ollama; import requests; import psutil; import dotenv" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Some dependencies are missing. Installing...
    pip install -r "%SCRIPT_DIR%\requirements.txt"
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✅ Python dependencies are installed

REM Check if .env file exists
echo 🔍 Checking environment configuration...
if not exist "%SCRIPT_DIR%\.env" (
    echo ⚠️ .env file not found. Creating template...
    echo GOOGLE_API_KEY=your_google_api_key_here > "%SCRIPT_DIR%\.env"
    echo GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id_here >> "%SCRIPT_DIR%\.env"
    echo BIG_MODEL_NAME=gemma3:12b >> "%SCRIPT_DIR%\.env"
    echo SMALL_MODEL_NAME=gemma3:1b >> "%SCRIPT_DIR%\.env"
    echo DEBUG=false >> "%SCRIPT_DIR%\.env"
    echo.
    echo ⚠️ Please edit the .env file with your actual API keys
    echo Opening .env file for editing...
    notepad "%SCRIPT_DIR%\.env"
    echo.
    echo Press any key when you've finished editing the .env file...
    pause >nul
)
echo ✅ Environment configuration exists

REM Check if global agent command is installed
echo 🔍 Checking global agent installation...
where agent >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Global agent command not found. Installing...
    call "%SCRIPT_DIR%\install_global_simple.bat"
    if %errorlevel% neq 0 (
        echo ❌ Failed to install global agent command
        pause
        exit /b 1
    )
) else (
    echo ✅ Global agent command is installed
)

echo.
echo 🎉 MCP Agent System is ready!
echo.
echo You can now use your agent with:
echo   agent "Your query here"
echo   agent -i  (for interactive mode)
echo.
echo Examples:
echo   agent "What is the latest news?"
echo   agent "List files in current directory"
echo   agent "Check Python version"
echo.

REM Offer to start interactive mode
set /p choice="Would you like to start interactive mode now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Starting interactive mode...
    agent -i
) else (
    echo.
    echo System is ready. Type 'agent --help' for usage information.
)

echo.
pause