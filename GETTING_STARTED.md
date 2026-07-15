# 🛣️ Highway Pilot - Getting Started

**Welcome!** You're about to launch a fully AI-powered logistics platform. Here's your step-by-step guide.

---

## 🚀 Choose Your Setup Method

### **Option 1: Automated Setup (Easiest) ⭐ RECOMMENDED**

#### Windows Users:

**PowerShell:**
```powershell
powershell -ExecutionPolicy Bypass -File QUICK_START.ps1
```

**Command Prompt:**
```cmd
QUICK_START.bat
```

#### Mac/Linux Users:
```bash
bash QUICK_START.sh
```

---

### **Option 2: Manual Setup**

If automated setup doesn't work, follow [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) (Windows) or [HIGHWAY_PILOT_SETUP.md](./HIGHWAY_PILOT_SETUP.md) (General).

---

## 📋 Prerequisites Checklist

Before running setup, ensure you have:

- [ ] **Python 3.9+** installed
  - Verify: `python --version`
  - Download: https://www.python.org/
  
- [ ] **Node.js 16+** installed  
  - Verify: `npm --version`
  - Download: https://nodejs.org/

- [ ] **API Keys** (get these first):
  - OpenAI: https://platform.openai.com/api-keys
  - Anthropic (optional): https://www.anthropic.com/api

---

## 🔧 Setup Steps

### Step 1: Run Setup Script

Choose your setup method above and run it. The script will:
- ✅ Create Python virtual environment
- ✅ Install all Python dependencies (47 packages)
- ✅ Install all Node packages
- ✅ Create `.env` configuration file

### Step 2: Configure API Keys

After setup completes, edit `backend/.env`:

```env
OPENAI_API_KEY=sk-your-key-here
```

Optional:
```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Step 3: Start the Backend Server

**Terminal 1:**
```powershell
cd PilotApp
.\.venv\Scripts\Activate.ps1    # or: .venv\Scripts\activate.bat on CMD
python -m uvicorn backend.app.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ **Backend is now running**

### Step 4: Start the Frontend Server

**Terminal 2:**
```powershell
cd pilot-web
npm run dev
```

You should see:
```
  VITE v4.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

✅ **Frontend is now running**

### Step 5: Open Application

Open your browser and visit:
## 🌐 **http://localhost:5173**

---

## 🎨 What You'll See

### Home Screen
- Welcome message
- AI Features overview
- Quick action buttons

### Sidebar Navigation
- 🤖 **AI Dashboard** - Main features
- 💬 **Chat** - AI chatbot interface
- 📍 **Route Optimizer** - Route planning
- 🚚 **Dispatch** - Job assignment
- 👥 **Driver Analytics** - Performance insights
- 🔧 **Maintenance** - Vehicle health
- 📈 **Forecasting** - Demand prediction
- 🛠️ **Settings** - Configuration

---

## 🧪 Testing Features

### 1. **AI Chat** 💬
- Type: "What jobs need to be dispatched?"
- Type: "Optimize a route from NYC to Boston"
- AI responds with intelligent suggestions

### 2. **Route Optimizer** 📍
- Add delivery stops (origin, destinations)
- Click "Optimize Route"
- Get optimized order with distance/time estimates

### 3. **Dispatch Dashboard** 🚚
- View available jobs and drivers
- Click "Auto Dispatch"
- AI assigns jobs to best drivers with confidence scores

### 4. **Driver Analytics** 👥
- Select a driver
- View performance metrics (safety, efficiency, customer service)
- Get AI insights about driver behavior

### 5. **Maintenance Predictor** 🔧
- Select a vehicle
- Get maintenance predictions by urgency
- See estimated costs and parts needed

---

## ✅ Verification Checklist

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:5173  
- [ ] API health check works
- [ ] AI Chat responds
- [ ] Route optimization works
- [ ] Dispatch assignment works
- [ ] Browser shows no errors (F12 to check)
- [ ] Console shows no CORS errors

---

## 🐛 Troubleshooting

### Browser shows "Connection Refused"
**Solution**: Make sure both servers are running
```powershell
# Terminal 1: Backend
python -m uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: Frontend  
npm run dev
```

### "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Activate virtual environment
```powershell
cd PilotApp
.\.venv\Scripts\Activate.ps1
```

### "npm: command not found"
**Solution**: Install Node.js from https://nodejs.org/

### Port 8000 or 5173 already in use
**Solution**: Use different ports
```powershell
# Backend on port 8001
python -m uvicorn backend.app.main:app --reload --port 8001

# Frontend on port 5174
npm run dev -- --port 5174
```

### CORS errors in browser console
**Solution**: Check backend is running and CORS is enabled

### Changes not reflecting
**Solution**: Both servers have auto-reload
- If not working, stop (Ctrl+C) and restart
- Clear browser cache (Ctrl+Shift+Delete)

For more help, see [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) or [HIGHWAY_PILOT_SETUP.md](./HIGHWAY_PILOT_SETUP.md).

---

## 📂 Project Structure

```
PilotApp/
├── 🚀 START HERE → This file (GETTING_STARTED.md)
├── 📖 Then read → README_HIGHWAY_PILOT.md
├── 🔧 Reference → WINDOWS_SETUP.md (Windows) or HIGHWAY_PILOT_SETUP.md (General)
├── 👨‍💻 Development → DEVELOPER_GUIDE.md
│
├── backend/
│   ├── .venv/                (Python virtual environment - created by setup)
│   ├── services/             (7 AI services)
│   ├── routes/ai_routes.py   (API endpoints)
│   ├── app/main.py           (FastAPI app)
│   ├── requirements.txt       (Dependencies)
│   └── .env                  (Configuration - edit with API keys)
│
└── pilot-web/
    ├── node_modules/         (Node packages - created by setup)
    ├── src/
    │   ├── components/       (React AI components)
    │   ├── App.jsx           (Main app)
    │   └── main.jsx          (Entry point)
    └── package.json          (Node dependencies)
```

---

## 🎓 Learning Path

### Beginner (Today)
1. ✅ Run setup script
2. ✅ Start both servers
3. ✅ Explore UI and test features
4. ✅ Try each AI component

### Intermediate (This Week)
1. Read [README_HIGHWAY_PILOT.md](./README_HIGHWAY_PILOT.md)
2. Review [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md)
3. Explore backend services in `backend/services/`
4. Explore React components in `pilot-web/src/components/`

### Advanced (This Month)
1. Study [HIGHWAY_PILOT_SETUP.md](./HIGHWAY_PILOT_SETUP.md)
2. Add your own AI features
3. Integrate with real database (PostgreSQL)
4. Deploy to production

---

## 🌟 Features at a Glance

| Feature | What It Does | Try This |
|---------|------------|-----------|
| **Route Optimizer** 📍 | AI calculates optimal delivery routes | Add 3 stops, click Optimize |
| **Dispatch** 🚚 | AI assigns jobs to drivers | Click "Auto Dispatch" |
| **Analytics** 👥 | AI analyzes driver performance | Select a driver |
| **Maintenance** 🔧 | AI predicts vehicle failures | Select a vehicle |
| **Forecasting** 📈 | AI predicts shipping demand | View demand trends |
| **Chat** 💬 | AI chatbot for operations | Ask a question |

---

## 🔌 API Quick Reference

All AI features are available as REST APIs:

```
GET  /api/ai/health                    ✅ System health
POST /api/ai/optimize-route            ✅ Route planning
POST /api/ai/auto-dispatch             ✅ Single job dispatch
POST /api/ai/batch-dispatch            ✅ Multiple job dispatch
POST /api/ai/predict-maintenance       ✅ Maintenance prediction
POST /api/ai/driver-analytics          ✅ Driver analysis
POST /api/ai/forecast-demand           ✅ Demand forecasting
POST /api/ai/chat                      ✅ AI chat
GET  /api/ai/chat-history              ✅ Chat history
GET  /api/ai/chat-suggestions          ✅ Suggestions
```

Test API: `curl http://localhost:8000/api/ai/health`

---

## 💾 File Structure After Setup

After running the setup script, your directory will have:

```
backend/
├── .venv/                          ← Virtual environment (created)
├── node_modules/ (if any)
├── requirements.txt                ← Dependencies list
├── .env                           ← Your configuration (created, edit this!)
├── .env.example                   ← Template
├── app/
├── services/                      ← 7 AI services
├── routes/
└── ...

pilot-web/
├── node_modules/                  ← Node packages (created)
├── src/
│   ├── components/               ← 5 React components
│   └── ...
├── package.json
└── ...
```

---

## 🚀 Next Steps

1. **Now**: Run setup script → Start servers → Open browser
2. **Today**: Test all AI features in the UI
3. **This Week**: Read developer documentation
4. **This Month**: Add custom AI features

---

## 📚 All Documentation

| Document | Purpose | Who Should Read |
|----------|---------|-----------------|
| **This file** | Getting started | Everyone first |
| [README_HIGHWAY_PILOT.md](./README_HIGHWAY_PILOT.md) | Project overview | Technical leads |
| [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) | Windows-specific guide | Windows users |
| [HIGHWAY_PILOT_SETUP.md](./HIGHWAY_PILOT_SETUP.md) | Complete setup guide | Deployment team |
| [DEVELOPER_GUIDE.md](./DEVELOPER_GUIDE.md) | How to extend | Developers |
| [INDEX.md](./INDEX.md) | Navigation guide | Everyone |

---

## ❓ FAQ

**Q: Do I need all the API keys?**
A: No, just OpenAI for now. Claude is optional (falls back to OpenAI).

**Q: Can I run just frontend or backend?**
A: Frontend needs backend to run. Backend can run standalone.

**Q: How do I stop the servers?**
A: Press `Ctrl+C` in each terminal.

**Q: Do I need PostgreSQL?**
A: No, it's optional. System can use SQLite by default.

**Q: Can I change the ports?**
A: Yes! Add `--port 8001` to uvicorn or `--port 5174` to npm run dev.

---

## 💬 Getting Help

1. Check the [Troubleshooting section](#-troubleshooting) above
2. Read [WINDOWS_SETUP.md](./WINDOWS_SETUP.md) for Windows issues
3. Read [HIGHWAY_PILOT_SETUP.md](./HIGHWAY_PILOT_SETUP.md) for general setup issues
4. Check browser console: F12 → Console tab
5. Check terminal output for error messages

---

## 🎯 Success Checklist

- [ ] Setup script ran without errors
- [ ] Backend server is running
- [ ] Frontend server is running
- [ ] Browser opens http://localhost:5173
- [ ] AI Chat component loads
- [ ] Can type in chat and get response
- [ ] All 5 UI components are accessible
- [ ] No errors in browser console (F12)

---

## 🎉 Ready to Go!

You now have a **production-ready AI logistics platform** with:
- ✅ 7 AI services
- ✅ 5 beautiful React components
- ✅ 11+ API endpoints
- ✅ Natural language interface
- ✅ Autonomous dispatch
- ✅ And much more!

**Let's start!** Run your setup script and open http://localhost:5173 🚀

---

**Highway Pilot** - Where AI Drives Logistics Forward! 🛣️🤖

Questions? Check [INDEX.md](./INDEX.md) for all documentation.
