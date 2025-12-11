@echo off
setlocal
set "BASE_DIR=%~dp0"
set "PYTHON="

rem Tenta usar py -3.11 se existir
py -3.11 -c "import sys; raise SystemExit(0)" >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON=py -3.11"
) else (
    rem Tenta python atual e checa versao
    python -c "import sys; exit(0 if sys.version_info>=(3,11) else 1)" >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON=python"
    ) else (
        echo Python 3.11 nao encontrado. Tentando instalar via winget...
        winget install -e --id Python.Python.3.11 --silent
        if %errorlevel%==0 (
            set "PYTHON=py -3.11"
        ) else (
            echo Falha ao instalar Python via winget. Instale manualmente o Python 3.11+ e reexecute este script.
            exit /b 1
        )
    )
)

echo Usando interpretador: %PYTHON%
echo Criando ambiente virtual em %BASE_DIR%\.venv ...
%PYTHON% -m venv "%BASE_DIR%\.venv"

echo Ativando ambiente virtual...
call "%BASE_DIR%\.venv\Scripts\activate.bat"

echo Instalando dependencias...
pip install --upgrade pip
pip install -r "%BASE_DIR%requirements.txt"

echo Instalacao concluida.
endlocal
