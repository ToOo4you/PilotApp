# Highway Pilot - Windows Setup Guide

## Quick Start for Windows Users

### Prerequisites

Before you begin, ensure you have installed:

1. **Python 3.9+** - Download from https://www.python.org/
   - ✅ During installation, check "Add Python to PATH"
   
2. **Node.js 16+** - Download from https://nodejs.org/
   - ✅ Use the LTS version (includes npm)

3. **Git** (optional) - Download from https://git-scm.com/

Verify installation by opening PowerShell and running:
```powershell
python --version
npm --version
```

---

## Option 1: Automated Setup (Recommended)

### Using PowerShell Script

```powershell
# Open PowerShell in the PilotApp directory
# Run this command:
powershell -ExecutionPolicy Bypass -File QUICK_START.ps1
```

The script will:
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies
- ✅ Install all Node dependencies
- ✅ Create .env configuration file

### Using Batch Script

```cmd
# Open Command Prompt in the PilotApp directory
# Run this command:
QUICK_START.bat
```

Same as PowerShell but in classic Command Prompt format.

---

## Option 2: Manual Setup

### Step 1: Backend Setup

```powershell
# Open PowerShell and navigate to PilotApp
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env with your API keys
notepad .env
```

### Step 2: Frontend Setup

```powershell
# Open new PowerShell window
cd pilot-web

# Install dependencies
npm install
```

---

## Step 3: Running the Application

### Terminal 1 - Backend Server

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2 - Frontend Dev Server

```powershell
cd pilot-web
npm run dev
```

You should see:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
```

### Step 4: Open in Browser

Visit: **http://localhost:5173**

---

## Configuration

### Setting Up API Keys

Edit `backend/.env`:

```env
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional (falls back to OpenAI if not set)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Database (optional - uses SQLite by default)
DATABASE_URL=postgresql://user:password@localhost/highway_pilot
```

Get API keys from:
- **OpenAI**: https://platform.openai.com/api-keys
- **Anthropic**: https://www.anthropic.com/api

---

## Testing the Installation

### Check Backend Health

```powershell
curl http://localhost:8000/api/ai/health
```

Or open in browser: http://localhost:8000/api/ai/health

Expected response:
```json
{"status":"ok","timestamp":"2026-07-10T..."}
```

### Test Route Optimization

```powershell
$body = @{
    stops = @(
        @{latitude = 40.7128; longitude = -74.0060; name = "NYC"},
        @{latitude = 40.7614; longitude = -73.9776; name = "Central Park"}
    )
    vehicle_type = "standard"
} | ConvertTo-Json

curl -X POST `
  -H "Content-Type: application/json" `
  -Body $body `
  http://localhost:8000/api/ai/optimize-route
```

---

## Troubleshooting

### Issue: "Python not found"
**Solution**: Add Python to PATH
1. Go to Settings → System → Environment Variables
2. Add `C:\Users\YourUsername\AppData\Local\Programs\Python\Python39\` to PATH
3. Restart PowerShell

### Issue: "npm not found"
**Solution**: Add Node.js to PATH
1. Reinstall Node.js from https://nodejs.org/
2. Check "Automatically install necessary tools for Node.js"
3. Restart PowerShell

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Ensure virtual environment is activated
```powershell
# Check if (venv) is shown in prompt
# If not, run:
.\.venv\Scripts\Activate.ps1
```

### Issue: "CORS error in browser"
**Solution**: Backend must be running
```powershell
# In Terminal 1, verify:
uvicorn app.main:app --reload --port 8000
```

### Issue: "Port already in use"
**Solution**: Change the port
```powershell
# Backend on different port
uvicorn app.main:app --reload --port 8001

# Update frontend to connect to new port
# Edit pilot-web/src/api.js and change fetch URL
```

### Issue: Script execution disabled
**Solution**: Allow PowerShell scripts
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Important Notes for Windows

### File Paths
- Use `\` for Windows paths
- Python accepts both `/` and `\`
- Always use quotes for paths with spaces: `"C:\Program Files\..."`

### Virtual Environment
- Activation script: `.\.venv\Scripts\Activate.ps1`
- For Command Prompt: `.venv\Scripts\activate.bat`
- For PowerShell: `.\.venv\Scripts\Activate.ps1`

### Environment Variables
- Edit `.env` with Notepad or any text editor
- Restart servers after changing `.env`
- Don't commit `.env` to git (it's in .gitignore)

---

## Development Workflow

### Making Changes

1. **Backend Changes**: Server auto-reloads with `--reload` flag
2. **Frontend Changes**: Browser auto-refreshes with Vite dev server
3. **API Changes**: Restart both servers

### Stopping Services

```powershell
# In PowerShell/Command Prompt:
# Press Ctrl+C to stop either server
```

### Deactivating Virtual Environment

```powershell
deactivate
```

---

## Next Steps

1. ✅ Run QUICK_START.ps1 or QUICK_START.bat
2. ✅ Add API keys to `backend\.env`
3. ✅ Start both servers
4. ✅ Open http://localhost:5173
5. ✅ Test each AI feature

---

## Documentation

- **Full Setup Guide**: [HIGHWAY_PILOT_SETUP.md](./HIGHWAY_PILOT_SETUP.md)
- **Project Overview**: [README_HIGHWAY_PILOT.md](./README_HIGHWAY_PILOT.md)
- **Developer Guide**: [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
- **Navigation Index**: [INDEX.md](./INDEX.md)

---

## Support

For issues:
1. Check this guide - Troubleshooting section
2. Check [HIGHWAY_PILOT_SETUP.md](./HIGHWAY_PILOT_SETUP.md)
3. Verify all prerequisites are installed
4. Check console output for error messages

---

## Common PowerShell Tips

### Check Current Directory
```powershell
pwd  # or Get-Location
```

### List Files
```powershell
ls  # or Get-ChildItem
```

### Navigate
```powershell
cd backend
cd ..
```

### Clear Screen
```powershell
cls
```

### Check Python Version
```powershell
python --version
python -c "import sys; print(sys.version)"
```

---

**Happy coding! 🚀 Welcome to Highway Pilot! 🛣️**
