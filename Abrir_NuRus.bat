@echo off
setlocal EnableExtensions DisableDelayedExpansion
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo NuRus no esta instalado en el entorno aislado.
  echo Ejecuta primero Instalar_NuRus.bat.
  pause
  exit /b 1
)

".venv\Scripts\python.exe" -m nurus.app
if errorlevel 1 (
  echo.
  echo NuRus termino con un error. Conserva este mensaje para diagnostico.
  pause
  exit /b 1
)
