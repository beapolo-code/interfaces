@echo off
title Servidor API Vigia SOS (PostgreSQL)
cd /d "%~dp0"

echo ========================================================
echo Iniciando Servidor API Vigia SOS con PostgreSQL
echo Puerto: 5000 (http://localhost:5000)
echo Base de Datos: Diseno de Interfaz (PostgreSQL 5432)
echo ========================================================
echo.

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    py api_server.py
    goto end
)

python api_server.py

:end
pause
