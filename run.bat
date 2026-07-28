@echo off
title TikTok Video Exploit Decoder & Repair Tool
chcp 65001 >nul
cls

echo ================================================================
echo          TikTok Video Exploit Decoder & Repair Tool
echo ================================================================
echo.

:: Check if file/folder was dropped onto .bat file
if "%~1" NEQ "" (
    echo [DRAG & DROP DETECTED]
    echo Input: %~1
    echo.
    python "%~dp0main.py" -i "%~1" -o "%~dp0output"
    echo.
    echo Processing finished. Press any key to exit.
    pause >nul
    exit /b
)

:MENU
cls
echo ================================================================
echo          TikTok Video Exploit Decoder & Repair Tool
echo ================================================================
echo [1] Process default 'input' folder (Output -> 'output')
echo [2] Enter custom Video File or Folder path
echo [3] Process default 'input' folder with 120 FPS target
echo [4] Check / Install Python Dependencies
echo [5] Exit
echo ================================================================
set /p choice="Select an option (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running repair on 'input' folder...
    python "%~dp0main.py" -i "%~dp0input" -o "%~dp0output"
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto MENU
)

if "%choice%"=="2" (
    echo.
    set /p custom_path="Enter full path to Video File or Folder: "
    python "%~dp0main.py" -i "%custom_path:"=%" -o "%~dp0output"
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto MENU
)

if "%choice%"=="3" (
    echo.
    echo Running repair on 'input' folder with 120 FPS target...
    python "%~dp0main.py" -i "%~dp0input" -o "%~dp0output" -fps 120
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto MENU
)

if "%choice%"=="4" (
    echo.
    echo Installing requirements...
    pip install -r "%~dp0requirements.txt"
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto MENU
)

if "%choice%"=="5" exit /b

goto MENU
