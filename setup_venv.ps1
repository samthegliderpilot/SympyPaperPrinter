param(
    [string]$VenvName = ".venv",
    [string]$Extras = "dev,notebook",
    [switch]$Recreate,
    [switch]$InstallKernel
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

if (!(Test-Path (Join-Path $ProjectRoot "pyproject.toml"))) {
    throw "pyproject.toml not found in $ProjectRoot. Run this from a Python project root."
}

$VenvPath = Join-Path $ProjectRoot $VenvName

if ($Recreate -and (Test-Path $VenvPath)) {
    Write-Host "Removing existing venv: $VenvPath" -ForegroundColor Yellow
    Remove-Item -Recurse -Force $VenvPath
}

if (!(Test-Path $VenvPath)) {
    Write-Host "Creating venv: $VenvPath" -ForegroundColor Green
    python -m venv $VenvPath
} else {
    Write-Host "Venv already exists: $VenvPath" -ForegroundColor DarkYellow
}

$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
Write-Host "Activating venv..." -ForegroundColor Green
& $ActivateScript

python -m pip install --upgrade pip

# Normalize extras: "dev,notebook" -> ".[dev,notebook]"
$Extras = $Extras.Trim()
if ($Extras -eq "" -or $Extras -eq "none") {
    Write-Host "Installing editable (no extras)..." -ForegroundColor Green
    pip install -e .
} else {
    # allow either "dev,notebook" or "[dev,notebook]"
    if ($Extras.StartsWith("[") -and $Extras.EndsWith("]")) {
        $ExtrasSpec = ".$Extras"
    } else {
        $ExtrasSpec = ".[{0}]" -f $Extras
    }
    Write-Host "Installing editable with extras: $ExtrasSpec" -ForegroundColor Green
    pip install --upgrade -e $ExtrasSpec
}

if ($InstallKernel) {
    Write-Host "Installing ipykernel + registering kernel..." -ForegroundColor Green
    pip install ipykernel
    $KernelName = (Split-Path -Leaf $ProjectRoot) -replace "\s+", "-"
    python -m ipykernel install --user --name $KernelName --display-name "Python ($KernelName)"
    Write-Host "Kernel registered as: Python ($KernelName)" -ForegroundColor Cyan
}

Write-Host "`nDone.`nActivate later with:`n  .\$VenvName\Scripts\Activate.ps1" -ForegroundColor Cyan
