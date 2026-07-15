# Highway Pilot - Quick Start Setup Script (Windows PowerShell)
# Run: powershell -ExecutionPolicy Bypass -File QUICK_START.ps1

Write-Host "🛣️  Highway Pilot - Quick Start Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Function to show colored messages
function Write-Success { Write-Host "✅ $args" -ForegroundColor Green }
function Write-Info { Write-Host "ℹ️  $args" -ForegroundColor Blue }
function Write-Warning { Write-Host "⚠️  $args" -ForegroundColor Yellow }
function Write-Step { Write-Host "📍 $args" -ForegroundColor Magenta }

# Step 1: Backend Setup
Write-Step "Step 1: Setting up Backend..."
Write-Host ""

# Ensure we are running from repository root
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

# Check if Python is installed
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Warning "Python not found. Please install Python 3.9+ from https://www.python.org/"
    exit 1
}

# Create virtual environment
Write-Info "Creating Python virtual environment..."
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Info "Installing Python dependencies (this may take a moment)..."
pip install -r backend\requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Setup environment
Write-Info "Setting up environment file..."
if (-not (Test-Path backend\.env)) {
    Copy-Item backend\.env.example backend\.env
    Write-Warning "Please edit .env with your API keys:"
    Write-Host "   - OPENAI_API_KEY" -ForegroundColor Yellow
    Write-Host "   - ANTHROPIC_API_KEY" -ForegroundColor Yellow
    Write-Host "   - DATABASE_URL (optional)" -ForegroundColor Yellow
} else {
    Write-Success ".env already exists"
}

Write-Host ""
Write-Success "Backend setup complete!"
Write-Host ""

# Step 2: Frontend Setup
Write-Step "Step 2: Setting up Frontend..."
Write-Host ""

# Navigate to frontend
Set-Location pilot-web

# Check if Node.js is installed
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Warning "Node.js/npm not found. Please install from https://nodejs.org/"
    exit 1
}

Write-Info "Installing Node dependencies (this may take a moment)..."
npm install --silent | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install Node dependencies" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Success "Frontend setup complete!"
Write-Host ""

# Step 3: Display startup instructions
Write-Step "Step 3: Ready to Start Services"
Write-Host ""
Write-Host "To start the application, open TWO separate PowerShell windows:"
Write-Host ""

Write-Host "Terminal 1 - Backend:" -ForegroundColor Yellow
Write-Host "  cd $repoRoot" -ForegroundColor White
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python -m uvicorn backend.app.main:app --reload --port 8000" -ForegroundColor White
Write-Host ""

Write-Host "Terminal 2 - Frontend:" -ForegroundColor Yellow
Write-Host "  cd $repoRoot\pilot-web" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""

Write-Host "Then open: " -ForegroundColor Cyan -NoNewline
Write-Host "http://localhost:5173" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Success "Setup Complete!"
Write-Host "════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Open backend/.env and add your API keys" -ForegroundColor White
Write-Host "2. Follow the startup instructions above" -ForegroundColor White
Write-Host "3. Open http://localhost:5173 in your browser" -ForegroundColor White
Write-Host "4. Start using Highway Pilot!" -ForegroundColor White
Write-Host ""

Write-Host "For detailed information, see:" -ForegroundColor Cyan
Write-Host "  - HIGHWAY_PILOT_SETUP.md - Full setup guide" -ForegroundColor White
Write-Host "  - README_HIGHWAY_PILOT.md - Project overview" -ForegroundColor White
Write-Host "  - DEVELOPER_GUIDE.md - How to extend" -ForegroundColor White
Write-Host "  - INDEX.md - Navigation guide" -ForegroundColor White
Write-Host ""

Write-Host "Happy coding! 🚀" -ForegroundColor Green
