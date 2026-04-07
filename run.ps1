# PowerShell wrapper to run Weather Platform with proper venv activation
# Usage: .\run.ps1 api | .\run.ps1 dashboard | .\run.ps1 pipeline

param(
    [string[]]$Arguments
)

# Get the script directory
$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Activate virtual environment
$VenvPath = Join-Path $ScriptDir ".venv"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

if (Test-Path $ActivateScript) {
    & $ActivateScript
} else {
    Write-Host "Virtual environment not found at: $VenvPath" -ForegroundColor Red
    Write-Host "Please create it with: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Change to project directory
Set-Location $ScriptDir

# Run the main script with arguments
$PythonPath = Join-Path $VenvPath "Scripts\python.exe"
& $PythonPath main.py @Arguments
