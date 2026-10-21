@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul
cd /d "%~dp0"
title Cartaviva - publicar en GitHub y Vercel

echo ==========================================================
echo   CARTAVIVA - publicar en GitHub y Vercel
echo ==========================================================
echo Este asistente usa TUS cuentas y hace tres cosas:
echo   1. Guarda el proyecto en Git (commit)
echo   2. Lo sube a tu GitHub
echo   3. Publica el esqueleto en tu Vercel y te da el link
echo.
echo Cuando se abra el navegador, inicia sesion y vuelve a esta ventana.
echo.
pause

rem ---------------------------------------------------------------
rem  Paso 0: programas necesarios (se instalan solos con winget)
rem ---------------------------------------------------------------
set FALTABA=0
call :herramienta git Git.Git "Git"
call :herramienta gh GitHub.cli "GitHub CLI"
call :herramienta node OpenJS.NodeJS.LTS "Node.js"
if "%FALTABA%"=="1" (
  echo.
  echo Se instalaron programas nuevos. CIERRA esta ventana y vuelve a abrir publicar.bat
  pause
  exit /b 0
)

rem ---------------------------------------------------------------
rem  Paso 1: Git (nombre, correo y commit)
rem ---------------------------------------------------------------
echo.
echo [1/3] Guardando el proyecto en Git...
set GNOMBRE=
set GCORREO=
for /f "delims=" %%a in ('git config --global user.name 2^>nul') do set GNOMBRE=%%a
for /f "delims=" %%a in ('git config --global user.email 2^>nul') do set GCORREO=%%a
if not defined GNOMBRE (
  set /p GNOMBRE=Escribe tu nombre completo para los commits:
  git config --global user.name "!GNOMBRE!"
)
if not defined GCORREO (
  set /p GCORREO=Escribe el correo de tu cuenta de GitHub:
  git config --global user.email "!GCORREO!"
)

if not exist ".git" git init -b main
git add -A
git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Cartaviva: ficha, esqueleto y MVP del Entregable 1"
) else (
  echo No hay cambios nuevos para guardar.
)

rem ---------------------------------------------------------------
rem  Paso 2: GitHub
rem ---------------------------------------------------------------
echo.
echo [2/3] Subiendo a GitHub...
call gh auth status >nul 2>nul
if errorlevel 1 (
  echo Se abrira el navegador para iniciar sesion en GitHub.
  call gh auth login --hostname github.com --git-protocol https --web
  if errorlevel 1 goto :error_github
)
call gh auth setup-git >nul 2>nul

git remote get-url origin >nul 2>nul
if not errorlevel 1 goto :empujar

set REPO=cartaviva
set /p REPO=Nombre del repositorio en GitHub (Enter = cartaviva):
call gh repo create "!REPO!" --public --source=. --remote=origin --push
if not errorlevel 1 goto :vercel

rem El repositorio ya existia en GitHub: lo conectamos y subimos
for /f "delims=" %%u in ('gh api user --jq .login') do set GHUSUARIO=%%u
git remote add origin "https://github.com/!GHUSUARIO!/!REPO!.git"

:empujar
git push -u origin main
if errorlevel 1 goto :error_github

rem ---------------------------------------------------------------
rem  Paso 3: Vercel (solo la carpeta esqueleto)
rem ---------------------------------------------------------------
:vercel
echo.
echo [3/3] Publicando el esqueleto en Vercel...
echo Si es la primera vez, elige "Continue with GitHub" para iniciar sesion.
pushd esqueleto
call npx --yes vercel@latest deploy --prod --yes
set RESULTADO=%errorlevel%
popd
if not "%RESULTADO%"=="0" goto :error_vercel

for /f "delims=" %%u in ('gh repo view --json url --jq .url 2^>nul') do set URLREPO=%%u
echo.
echo ==========================================================
echo   LISTO
echo   Repositorio en GitHub: !URLREPO!
echo   Link del esqueleto: la linea "Production" o "Aliased" de arriba
echo   (termina en .vercel.app). Abrela en el celular.
echo.
echo   Para actualizar despues de cambiar algo, vuelve a abrir publicar.bat
echo ==========================================================
pause
exit /b 0

rem ---------------------------------------------------------------
:herramienta
where %1 >nul 2>nul
if not errorlevel 1 exit /b 0
echo.
echo Falta %~3. Instalandolo con winget (acepta si Windows pide permiso)...
where winget >nul 2>nul
if errorlevel 1 (
  echo [ERROR] No se encontro winget. Instala %~3 a mano y vuelve a abrir este archivo.
  pause
  exit 1
)
winget install --id %2 -e --accept-source-agreements --accept-package-agreements
set FALTABA=1
exit /b 0

:error_github
echo.
echo [ERROR] No se pudo subir a GitHub. Revisa que iniciaste sesion y vuelve a abrir publicar.bat
pause
exit /b 1

:error_vercel
echo.
echo [ERROR] No se pudo publicar en Vercel. Vuelve a abrir publicar.bat
echo Si sigue fallando, usa la opcion manual de la seccion 6 del README.
pause
exit /b 1
