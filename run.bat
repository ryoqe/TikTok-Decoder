@echo off
title TikTok Video Exploit Decoder & Repair Tool v1.2.0
chcp 65001 >nul
cls

echo ================================================================
echo          TikTok Video Exploit Decoder & Repair Tool v1.2.0
echo ================================================================
echo.

:: Check if file/folder was dropped onto .bat file
if "%~1" NEQ "" (
    echo [DRAG & DROP DETECTED]
    echo Input: %~1
    echo.
    python "%~dp0main.py" -i "%~1" -o "%~dp0output" --gpu
    echo.
    echo Processing finished. Press any key to exit.
    pause >nul
    exit /b
)

:MENU
cls
echo ================================================================
echo          TikTok Video Exploit Decoder & Repair Tool v1.2.0
echo ================================================================
echo [1] 🖥️ Launch Desktop GUI App (Window Interface)
echo [2] 🚀 Process default 'input' folder (GPU Accelerated)
echo [3] 📁 Enter custom Video File or Folder path
echo [4] 🎬 Process default 'input' folder with 120 FPS target
echo [5] 📦 Install / Check Python Dependencies
echo [6] 🚪 Exit
echo ================================================================
set /p choice="Select an option (1-6): "

if "%choice%"=="1" (
    echo.
    echo Launching Desktop GUI App...
    python "%~dp0gui.py"
    goto MENU
)

if "%choice%"=="2" (
    echo.
    echo Running repair on 'input' folder (GPU Accelerated)...
    python "%~dp0main.py" -i "%~dp0input" -o "%~dp0output" --gpu
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto MENU
)

if "%choice%"=="3" (
    echo.
    set /p custom_path="Enter full path to Video File or Folder: "
    python "%~dp0main.py" -i "%custom_path:"=%" -o "%~dp0output" --gpu
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto MENU
)

if "%choice%"=="4" (
    echo.
    echo Running repair on 'input' folder with 120 FPS target...
    python "%~dp0main.py" -i "%~dp0input" -o "%~dp0output" -fps 120 --gpu
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto MENU
)

if "%choice%"=="5" (
    echo.
    echo Installing requirements...
    pip install -r "%~dp0requirements.txt"
    echo.
    echo Press any key to return to menu...
    pause >nul
    goto MENU
)

if "%choice%"=="6" exit /b

goto MENU
