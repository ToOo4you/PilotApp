# 🧠 EduLearn AI — Educational Platform for Diverse Learners

An AI-powered educational platform built specifically for students with **autism, ADHD, dyslexia, dyscalculia, and sensory processing differences**.

> **Completely separate from Highway Pilot.** This is a standalone app in the `edulearn/` directory.

---

## ✨ Features

| Feature | Description |
|---|---|
| 👤 **Learner Profile** | Set up a full learning profile — needs, interests, style, strengths |
| 📚 **AI Lesson Generator** | AI creates a personalised, step-by-step lesson on any topic |
| 🤖 **AI Tutor Chat** | Patient, warm, always-available AI tutor adapted to the learner |
| 🧠 **Adaptive Quiz** | AI generates quizzes tailored to the learner's level and style |
| 📈 **Progress Tracker** | Sessions, badges, streaks, and AI-generated progress insights |
| 🎨 **Sensory Settings** | Colour themes, font sizes, reduced animations, dyslexic font |

---

## 🗂️ Project Structure

```
edulearn/
├── backend/
│   ├── main.py                      # FastAPI app (port 8001)
│   ├── requirements.txt
│   ├── .env.example
│   ├── services/
│   │   ├── ai_service.py            # OpenAI / Anthropic / mock
│   │   └── education_service.py     # lesson, tutor, quiz, progress
│   └── routes/
│       └── education.py             # REST API endpoints
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css                # Global sensory-friendly styles
│   │   ├── lib/
│   │   │   ├── api.js               # Backend API client
│   │   │   └── useSensorySettings.js # CSS-variable theming hook
│   │   └── components/
│   │       ├── EducationHub.jsx     # Main shell + dashboard
│   │       ├── LearnerProfile.jsx   # Profile setup
│   │       ├── AITutor.jsx          # Chat tutor
│   │       ├── AdaptiveLesson.jsx   # Lesson viewer + quiz
│   │       ├── ProgressTracker.jsx  # Stats, badges, AI insights
│   │       └── SensoryPanel.jsx     # Display accessibility settings
│   ├── vite.config.js               # Port 5174
│   └── package.json
│
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── nginx.conf
```

---

## 🚀 Quick Start (Local Development)

### 1. Backend

```bash
cd edulearn/backend

# Copy and configure environment
cp .env.example .env
# Edit .env — add OPENAI_API_KEY or leave AI_MOCK_MODE=true for offline use

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server (from repo root, so package imports work)
cd ../..
uvicorn edulearn.backend.main:app --reload --port 8001
```

API docs available at: **http://localhost:8001/docs**

### 2. Frontend

```bash
cd edulearn/frontend
npm install
npm run dev
```

Open: **http://localhost:5174**

---

## 🐳 Docker (Full Stack)

```bash
cd edulearn

# Optional: add real API keys
export OPENAI_API_KEY=sk-...

docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:4174 |
| Backend API | http://localhost:8001 |
| API Docs | http://localhost:8001/docs |

---

## 🔑 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic Claude API key |
| `AI_MODEL_PRIMARY` | `openai` | Which provider to use first |
| `AI_MOCK_MODE` | `true` | Use built-in mock responses (no key needed) |
| `CORS_ORIGINS` | localhost:5174 | Allowed frontend origins |

> **No API key?** Set `AI_MOCK_MODE=true` (the default in development). The app works fully with rich mock responses.

---

## 🧩 Neurodiversity-First Design

| Need | Accommodations Built-In |
|---|---|
| **Autism** | Predictable structure, explicit instructions, no ambiguity |
| **ADHD** | Short chunked activities, break reminders, focus mode |
| **Dyslexia** | Dyslexic-friendly font option, short sentences, large text |
| **Dyscalculia** | Visual examples, real-world connections, step-by-step |
| **Sensory** | Calm / high-contrast themes, reduced animations |

---

## 📡 API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/education/lesson/generate` | Generate personalised lesson |
| `POST` | `/api/education/tutor/chat` | Chat with AI tutor |
| `POST` | `/api/education/quiz/generate` | Generate adaptive quiz |
| `POST` | `/api/education/progress/analyze` | AI progress insights |
| `GET`  | `/api/education/health` | Health check |

---

## 🛠️ Tech Stack

- **Backend**: Python · FastAPI · OpenAI GPT-4 · Anthropic Claude
- **Frontend**: React 18 · Vite · CSS custom properties (sensory theming)
- **Deployment**: Docker · Nginx
