@echo off
setlocal
set "FOUND=0"

rem Encerra processos cujo comando contenha src.bot.main
for /f "skip=1 tokens=1" %%p in ('wmic process where "CommandLine like '%%src.bot.main%%'" get ProcessId 2^>nul') do (
    if not "%%p"=="" (
        set "FOUND=1"
        echo Encerrando PID %%p
        taskkill /PID %%p /T /F >nul 2>&1
    )
)

if "%FOUND%"=="0" (
    echo Nenhum processo do bot encontrado.
) else (
    echo Finalizado.
)

pause
endlocal
