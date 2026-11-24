@echo off
title SEGURIDAD SOS - KivyMD Mobile App
cd /d "%~dp0"

echo ========================================================
echo Iniciando SEGURIDAD SOS - MODO MOVIL (414x896)
echo ========================================================
echo.

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Ejecutando con py launcher...
    py mobile\main.py
    goto end
)

if exist "C:\Users\hp\AppData\Local\Programs\Python\Python310\python.exe" (
    echo Ejecutando con Python 3.10 directo...
    "C:\Users\hp\AppData\Local\Programs\Python\Python310\python.exe" mobile\main.py
    goto end
)

where python >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Ejecutando con python...
    python mobile\main.py
    goto end
)

echo [ERROR] No se pudo encontrar el ejecutable de Python.
echo Asegurate de tener Python instalado o py en tu sistema.

:end
echo.
pause
