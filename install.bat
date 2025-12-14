@echo off
echo ============================================
echo    Cotizador Pro - Instalador/Actualizador
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo Por favor, instale Python 3.9 o superior desde https://python.org
    pause
    exit /b 1
)

echo [INFO] Python encontrado.
echo.

REM ============================================
REM   GIT UPDATE SECTION
REM ============================================
echo [INFO] Verificando actualizaciones del repositorio...
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Git no esta instalado. Saltando actualizacion.
    echo         Para actualizar automaticamente, instale Git desde https://git-scm.com
    echo.
    goto :install_deps
)

REM Check if this is a git repository
if not exist ".git" (
    echo [INFO] Inicializando repositorio Git...
    git init
    git remote add origin https://github.com/Gerlex-Core/Cotizador.git
)

REM Fetch latest changes
echo [INFO] Descargando actualizaciones desde GitHub...
git fetch origin main 2>nul
if errorlevel 1 (
    git fetch origin master 2>nul
)

REM Pull latest changes (stash local changes first)
echo [INFO] Aplicando actualizaciones...
git stash -q 2>nul
git pull origin main 2>nul
if errorlevel 1 (
    git pull origin master 2>nul
)
git stash pop -q 2>nul

echo [OK] Proyecto actualizado!
echo.

:install_deps
REM ============================================
REM   DEPENDENCY INSTALLATION
REM ============================================

REM Upgrade pip first
echo [INFO] Actualizando pip...
python -m pip install --upgrade pip

echo.
echo [INFO] Instalando dependencias...
echo.

REM Install from requirements.txt
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un error instalando las dependencias.
    echo Intente ejecutar manualmente: pip install PyQt6 reportlab
    pause
    exit /b 1
)

echo.
echo ============================================
echo    Instalacion completada exitosamente!
echo ============================================
echo.
echo Repositorio: https://github.com/Gerlex-Core/Cotizador.git
echo.
echo Para ejecutar la aplicacion, use:
echo    python main.py
echo.
echo O haga doble clic en "run.bat"
echo.
pause
