@echo off
echo Iniciando Cotizador Pro...
python main.py
if errorlevel 1 (
    echo.
    echo [ERROR] La aplicacion no pudo iniciar.
    echo Asegurese de haber ejecutado install.bat primero.
    pause
)
