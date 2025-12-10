@echo off
setlocal
set BASE_DIR=%~dp0

if exist "%BASE_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON=%BASE_DIR%\.venv\Scripts\python.exe"
) else (
    set "PYTHON=python"
)

pushd "%BASE_DIR%"
rem Abre uma nova janela de console e mantem aberta apos rodar o bot
start "Discord Bot" cmd /k ""%PYTHON%" -m src.bot.main"
popd

endlocal
