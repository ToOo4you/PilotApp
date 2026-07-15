# Highway Pilot deploy validation (Windows PowerShell)
# Usage examples:
#   powershell -ExecutionPolicy Bypass -File .\DEPLOY_VALIDATE.ps1
#   powershell -ExecutionPolicy Bypass -File .\DEPLOY_VALIDATE.ps1 -ApiBaseUrl https://pilotapp.onrender.com -WebBaseUrl https://www.highwaypilotai.com

param(
    [string]$ApiBaseUrl = "",
    [string]$WebBaseUrl = ""
)

$ErrorActionPreference = "Stop"

function Write-Section([string]$message) {
    Write-Host ""
    Write-Host "== $message ==" -ForegroundColor Cyan
}

function Write-Ok([string]$message) {
    Write-Host "[OK] $message" -ForegroundColor Green
}

function Write-Warn([string]$message) {
    Write-Host "[WARN] $message" -ForegroundColor Yellow
}

function Invoke-Check([string]$url, [string]$label, [int]$timeoutSec = 10) {
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -UseBasicParsing -TimeoutSec $timeoutSec
        if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
            Write-Ok "$label ($($response.StatusCode))"
            return $true
        }

        Write-Warn "$label returned status $($response.StatusCode)"
        return $false
    } catch {
        Write-Warn "$label failed: $($_.Exception.Message)"
        return $false
    }
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$backendHealth = "http://127.0.0.1:8000/api/ai/health"
$frontendHealth = "http://127.0.0.1:5173"
$allPassed = $true

Write-Section "Local build + smoke validation"
if (-not (Test-Path $pythonExe)) {
    throw "Python virtual environment not found at $pythonExe"
}

Push-Location $repoRoot
& $pythonExe -m compileall backend | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Backend compile check failed"
}
Write-Ok "Backend compile check"

& $pythonExe -m unittest backend/tests/test_smoke.py -v
if ($LASTEXITCODE -ne 0) {
    throw "Backend smoke tests failed"
}
Write-Ok "Backend smoke tests"
Pop-Location

Write-Section "Live local services"
if (-not (Invoke-Check -url $backendHealth -label "Backend health")) {
    $allPassed = $false
}

if (-not (Invoke-Check -url $frontendHealth -label "Frontend URL")) {
    $allPassed = $false
}

if ($ApiBaseUrl) {
    Write-Section "Remote API validation"
    if (-not (Invoke-Check -url "$($ApiBaseUrl.TrimEnd('/'))/api/ai/health" -label "Remote API health")) {
        $allPassed = $false
    }
}

if ($WebBaseUrl) {
    Write-Section "Remote web validation"
    if (-not (Invoke-Check -url $WebBaseUrl -label "Remote web URL")) {
        $allPassed = $false
    }
}

Write-Section "Result"
if ($allPassed) {
    Write-Ok "Deploy validation passed"
    exit 0
}

Write-Warn "Deploy validation completed with warnings"
exit 1
