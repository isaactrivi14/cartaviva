@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Cartaviva - servidor local

echo ============================================
echo   CARTAVIVA - instalacion y arranque
echo ============================================

set PY=python
where python >nul 2>nul
if errorlevel 1 (
  where py >nul 2>nul
  if errorlevel 1 (
    echo.
    echo [ERROR] No se encontro Python.
    echo Instala Python 3.12 o superior desde https://www.python.org/downloads/
    echo y marca la casilla "Add python.exe to PATH" durante la instalacion.
    pause
    exit /b 1
  )
  set PY=py
)

if not exist .venv (
  echo [1/5] Creando entorno virtual .venv ...
  %PY% -m venv .venv || (echo [ERROR] No se pudo crear el entorno virtual & pause & exit /b 1)
)
call .venv\Scripts\activate.bat

echo [2/5] Instalando dependencias (la primera vez tarda unos minutos) ...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt || (echo [ERROR] Fallo la instalacion de dependencias. Revisa tu conexion a internet. & pause & exit /b 1)

if not exist .env (
  echo [3/5] Creando archivo .env a partir de .env.example ...
  copy .env.example .env >nul
)

echo [4/5] Creando tablas y cargando datos de demostracion ...
python manage.py migrate || (echo [ERROR] No se pudo conectar a la base de datos. Revisa el archivo .env & pause & exit /b 1)
python manage.py cargar_demo

echo.
echo [5/5] Listo. Abriendo http://127.0.0.1:8000
echo Para detener el servidor presiona CTRL + C en esta ventana.
echo.
start "" http://127.0.0.1:8000
python manage.py runserver
pause
