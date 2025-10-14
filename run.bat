@echo off
setlocal

REM ==========================
REM CONFIGURACIÓN
REM ==========================
set VENV_DIR=venv
set PYTHON_EXE=%VENV_DIR%\Scripts\python.exe
set SCRIPT=script.py

REM ==========================
REM CREAR VENV SI NO EXISTE
REM ==========================
if not exist %VENV_DIR% (
    echo Creando entorno virtual...
    python -m venv %VENV_DIR%
    %VENV_DIR%\Scripts\pip install --upgrade pip
    %VENV_DIR%\Scripts\pip install -r requirements.txt
)

REM ==========================
REM EJECUTAR SCRIPT
REM ==========================
%PYTHON_EXE% %SCRIPT%

pause
