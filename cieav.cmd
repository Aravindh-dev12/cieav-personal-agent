@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=python"

if "%1"=="chat" (
    shift
    "%PYTHON_EXE%" "%SCRIPT_DIR%python\cieav_platform\chat_cli.py" %*
) else (
    "%PYTHON_EXE%" -m commit_layer.cli %*
)
endlocal
