@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ========================================
echo NuRus - instalacion local aislada
echo ========================================

call :find_python
if not defined NURUS_PYTHON goto :no_python

echo Python 3.12 detectado: %NURUS_PYTHON%

if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>&1
  if errorlevel 1 goto :wrong_venv
) else (
  echo Creando entorno virtual .venv...
  %NURUS_PYTHON% -m venv .venv
  if errorlevel 1 goto :error
)

echo Instalando NuRus y soporte Excel / Outlook...
".venv\Scripts\python.exe" -m pip install -e ".[excel-legacy,excel-native,outlook]"
if errorlevel 1 goto :error

".venv\Scripts\python.exe" -m pip check
if errorlevel 1 goto :error

".venv\Scripts\python.exe" -c "import pandas, openpyxl, xlrd, win32com.client, nurus; print('NuRus instalado correctamente en el entorno aislado.')"
if errorlevel 1 goto :error

echo.
echo Instalacion terminada. Usa Abrir_NuRus.bat para iniciar.
pause
exit /b 0

:find_python
set "NURUS_PYTHON="
call :try_python py -3.12
if not defined NURUS_PYTHON call :try_python python
if not defined NURUS_PYTHON call :try_python python3.12
if not defined NURUS_PYTHON if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" call :try_python "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined NURUS_PYTHON if exist "%ProgramFiles%\Python312\python.exe" call :try_python "%ProgramFiles%\Python312\python.exe"
exit /b 0

:try_python
%* -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>&1
if not errorlevel 1 set "NURUS_PYTHON=%*"
exit /b 0

:wrong_venv
echo.
echo ERROR: existe .venv, pero no usa Python 3.12.
echo Renombra o elimina esa carpeta solo si no contiene trabajo pendiente y vuelve a ejecutar el instalador.
pause
exit /b 1

:no_python
echo.
echo ERROR: no se encontro un ejecutable de Python 3.12.
echo Se probo py -3.12, python, python3.12 y las rutas estandar por usuario.
echo Instala Python 3.12 para tu usuario o solicita soporte institucional antes de continuar.
pause
exit /b 1

:error
echo.
echo ERROR: la instalacion no termino correctamente.
echo Revisa el mensaje anterior. No se modifican politicas de Windows ni controles institucionales.
pause
exit /b 1
