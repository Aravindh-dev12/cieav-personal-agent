<#
.SYNOPSIS
    CIEAV Sovereign Personal Agent Native PowerShell Launcher.
    Runs without triggering Windows Application Control / WDAC .exe blocks.
#>

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "[ERROR] Python is not found in PATH. Please install Python 3.10+"
    exit 1
}

# If user specifies 'chat', launch interactive chat interface
if ($args.Count -gt 0 -and $args[0] -eq "chat") {
    $remaining = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
    python (Join-Path $ScriptDir "python\cieav_platform\chat_cli.py") @remaining
} else {
    # Default to commit_layer CLI (supports ask, model, work, review, undo, personal-agent, etc.)
    python -m commit_layer.cli @args
}
