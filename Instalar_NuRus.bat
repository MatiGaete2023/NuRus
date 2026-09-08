@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo NuRus - instalacion local aislada
echo ========================================

py -3.12 --version >nul 2>&1
if errorlevel 1 goto :no_python

if not exist ".venv\Scripts\python.exe" (
  echo Creando entorno virtual .venv...
  py -3.12 -m venv .venv
  if errorlevel 1 goto :error
)

echo Instalando NuRus y soporte Excel legacy / Outlook...
".venv\Scripts\python.exe" -m pip install -e ".[excel-legacy,outlook]"
if errorlevel 1 goto :error

".venv\Scripts\python.exe" -m pip check
if errorlevel 1 goto :error

".venv\Scripts\python.exe" -c "import pandas, openpyxl, xlrd, nurus; print('NuRus instalado correctamente en el entorno aislado.')"
if errorlevel 1 goto :error

echo.
echo Instalacion terminada. Usa Abrir_NuRus.bat para iniciar.
pause
exit /b 0

:no_python
echo.
echo ERROR: no se encontro Python 3.12 mediante el comando py -3.12.
echo Instala Python 3.12 o solicita soporte institucional antes de continuar.
pause
exit /b 1

:error
echo.
echo ERROR: la instalacion no termino correctamente.
echo Revisa el mensaje anterior. No se modifican politicas de Windows ni controles institucionales.
pause
exit /b 1
