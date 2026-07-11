# Highway Pilot - Quick Verification Script (Windows PowerShell)
# Run: powershell -ExecutionPolicy Bypass -File QUICK_CHECK.ps1

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$frontendDir = Join-Path $repoRoot "pilot-web"

$backendStartedByScript = $false
$backendProcess = $null

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

function Ensure-FrontendDeps {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        throw "npm is not installed or not available in PATH"
    }

    Push-Location $frontendDir
    if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
        Write-Warn "Frontend dependencies missing. Installing with npm ci..."
        npm ci
        if ($LASTEXITCODE -ne 0) { throw "npm ci failed" }
        Write-Ok "Frontend dependencies installed"
    }
    Pop-Location
}

function Test-BackendOnline {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/" -Method Get -TimeoutSec 2
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-BackendIfNeeded {
    if (Test-BackendOnline) {
        Write-Ok "Backend already running on http://127.0.0.1:8000"
        return
    }

    Write-Warn "Backend not detected. Starting backend temporarily..."
    Push-Location $repoRoot
    $script:backendProcess = Start-Process -FilePath $pythonExe -ArgumentList "-m uvicorn backend.app.main:app --port 8000" -PassThru -WorkingDirectory $repoRoot
    Pop-Location
    $script:backendStartedByScript = $true

    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 500
        if (Test-BackendOnline) {
            Write-Ok "Backend started successfully"
            return
        }
    }

    throw "Backend failed to start within timeout"
}

function Stop-BackendIfStarted {
    if ($script:backendStartedByScript -and $script:backendProcess -and -not $script:backendProcess.HasExited) {
        Write-Warn "Stopping temporary backend process..."
        Stop-Process -Id $script:backendProcess.Id -Force
        Write-Ok "Temporary backend stopped"
    }
}

try {
    Write-Section "Highway Pilot Quick Check"

    if (-not (Test-Path $pythonExe)) {
        throw "Python executable not found at $pythonExe"
    }
    Write-Ok "Using Python: $pythonExe"

    Write-Section "Backend compile check"
    Push-Location $repoRoot
    & $pythonExe -m compileall backend
    if ($LASTEXITCODE -ne 0) { throw "Compile check failed" }
    Pop-Location
    Write-Ok "Compile check passed"

    Write-Section "Backend runtime checks"
    Start-BackendIfNeeded

    Push-Location $repoRoot
    & $pythonExe -m unittest backend/tests/test_smoke.py -v
    if ($LASTEXITCODE -ne 0) { throw "Smoke tests failed" }
    Write-Ok "Smoke tests passed"

    & $pythonExe backend/scripts/health_check.py
    if ($LASTEXITCODE -ne 0) { throw "Health check failed" }
    Write-Ok "Health check passed"
    Pop-Location

    Write-Section "Frontend production build"
    Ensure-FrontendDeps
    Push-Location $frontendDir
    npm run build
    if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
    Pop-Location
    Write-Ok "Frontend build passed"

    Write-Section "Result"
    Write-Host "All quick checks passed." -ForegroundColor Green
    exit 0
} catch {
    Write-Host ""
    Write-Host "Quick check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Stop-BackendIfStarted
}
