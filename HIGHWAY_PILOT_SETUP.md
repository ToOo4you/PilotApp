# Highway Pilot - AI-Powered Logistics Platform

## 🚀 Quick Start Guide

Highway Pilot is a **fully AI-automated logistics application** designed for trucking, towing, shipping, and logistics operations. All dispatching, route planning, and operational decisions are powered by advanced AI models.

---

## 📋 Features

### 🤖 AI-Powered Automation
- **Route Optimization** - AI calculates optimal routes considering traffic, distance, and priorities
- **Autonomous Dispatch** - AI automatically assigns jobs to the best available driver
- **Predictive Maintenance** - AI predicts vehicle failures before they happen
- **Driver Analytics** - AI analyzes driver performance with detailed insights
- **Demand Forecasting** - AI predicts shipping demand and capacity needs
- **Natural Language Chat** - Conversational AI interface for dispatch operations

### 📊 Real-Time Operations
- Live tracking and monitoring
- Automated decision-making
- Performance analytics
- Predictive insights
- Risk alerts

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+
- Redis (for task queue)

### Backend Setup

#### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

**Required API Keys:**
- `OPENAI_API_KEY` - For GPT-4 models
- `ANTHROPIC_API_KEY` - For Claude models (optional fallback)
- `DATABASE_URL` - PostgreSQL connection string

#### 3. Set Up Database
```bash
# Using PostgreSQL
createdb highway_pilot

# Run migrations (if using Alembic)
alembic upgrade head
```

#### 4. Start Backend Server
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

#### 1. Install Node Dependencies
```bash
cd pilot-web
npm install
```

#### 2. Start Development Server
```bash
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## 🔌 API Endpoints

### AI Services (`/api/ai/`)

#### Route Optimization
```
POST /api/ai/optimize-route
- stops: List of delivery locations
- vehicle_type: Type of vehicle
- Returns: Optimized route with distance and time estimates
```

#### Autonomous Dispatch
```
POST /api/ai/auto-dispatch
- job: Job details
- available_drivers: List of available drivers
- Returns: Best driver assignment with confidence score

POST /api/ai/batch-dispatch
- jobs: Multiple jobs
- available_drivers: List of drivers
- optimization_strategy: "balanced", "maximize_utilization", or "minimize_eta"
```

#### Predictive Maintenance
```
POST /api/ai/predict-maintenance
- vehicle_data: Vehicle sensor and operational data
- Returns: List of predicted maintenance issues with urgency and cost
```

#### Driver Analytics
```
POST /api/ai/driver-analytics/{driver_id}
- metrics: Driver performance metrics
- Returns: Detailed performance analysis and insights
```

#### Demand Forecasting
```
POST /api/ai/forecast-demand
- historical_data: Past shipment data
- forecast_horizon_days: Number of days to forecast
- Returns: Demand predictions with confidence levels
```

#### AI Chat
```
POST /api/ai/chat
- session_id: Chat session identifier
- message: User message
- Returns: AI response with suggested actions

GET /api/ai/chat-history/{session_id}
- Returns: Conversation history

GET /api/chat-suggestions/{session_id}
- Returns: Suggested next actions
```

#### Health Check
```
GET /api/ai/health
- Returns: Status of all AI services
```

---

## 💬 AI Chat Examples

### Route Optimization
```
User: "Optimize route for 5 deliveries in Manhattan"
AI: [Analyzes traffic, distance, priorities] → Provides optimal route order
```

### Dispatch
```
User: "Assign job JOB-123 to best available driver"
AI: [Analyzes driver capacity, location, experience] → Assigns to optimal driver
```

### Maintenance
```
User: "Check maintenance status for all vehicles"
AI: [Analyzes sensor data] → Predicts failures and recommends actions
```

### Driver Insights
```
User: "Show performance analytics for John Smith"
AI: [Analyzes metrics] → Provides safety, efficiency, and retention scores
```

---

## 🏗️ Architecture

### Backend Stack
- **Framework**: FastAPI
- **AI Models**: OpenAI GPT-4, Anthropic Claude
- **Database**: PostgreSQL
- **Cache/Queue**: Redis + Celery
- **ML**: scikit-learn, TensorFlow
- **Embeddings**: Pinecone/ChromaDB

### Frontend Stack
- **Framework**: React + Vite
- **State**: React Hooks
- **Real-time**: WebSocket
- **Maps**: Leaflet/Google Maps
- **Styling**: CSS + Responsive Design

### AI Services Layer
1. **ai_service.py** - Core AI provider abstraction (OpenAI, Claude)
2. **route_optimizer.py** - Route optimization engine
3. **dispatch_service.py** - Autonomous dispatch logic
4. **maintenance_service.py** - Predictive maintenance
5. **driver_analytics.py** - Driver performance analysis
6. **forecasting_service.py** - Demand forecasting
7. **chatbot_service.py** - Conversational AI interface

---

## 📁 Project Structure

```
PilotApp/
├── backend/
│   ├── app/
│   │   └── main.py          # FastAPI app entry point
│   ├── auth/
│   │   └── security.py      # Authentication
│   ├── database/
│   │   ├── db.py           # Database config
│   │   └── models.py       # SQLAlchemy models
│   ├── routes/
│   │   ├── ai_routes.py    # AI endpoints (NEW)
│   │   ├── auth.py
│   │   ├── companies.py
│   │   ├── customers.py
│   │   ├── drivers.py
│   │   ├── jobs.py
│   │   ├── trailers.py
│   │   └── trucks.py
│   ├── services/
│   │   ├── ai_service.py              # AI provider (NEW)
│   │   ├── route_optimizer.py         # Route optimization (NEW)
│   │   ├── dispatch_service.py        # Dispatch system (NEW)
│   │   ├── maintenance_service.py     # Maintenance prediction (NEW)
│   │   ├── driver_analytics.py        # Driver analytics (NEW)
│   │   ├── forecasting_service.py     # Demand forecasting (NEW)
│   │   └── chatbot_service.py         # AI chatbot (NEW)
│   ├── requirements.txt
│   └── .env.example
│
├── pilot-web/
│   ├── src/
│   │   ├── App.jsx          # Updated with AI components
│   │   ├── App.css
│   │   ├── main.jsx
│   │   ├── index.css
│   │   └── components/
│   │       ├── AIChat.jsx               # Chat interface (NEW)
│   │       ├── AIChat.css
│   │       ├── RouteOptimizer.jsx       # Route optimization (NEW)
│   │       ├── RouteOptimizer.css
│   │       ├── DispatchDashboard.jsx    # Dispatch system (NEW)
│   │       ├── DispatchDashboard.css
│   │       ├── DriverAnalytics.jsx      # Driver analytics (NEW)
│   │       ├── DriverAnalytics.css
│   │       ├── MaintenancePredictor.jsx # Maintenance (NEW)
│   │       └── MaintenancePredictor.css
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   ├── SETUP.md (THIS FILE)
│   └── VISION.md
│
└── README.md
```

---

## 🔑 Configuration

### Environment Variables (.env)

```env
# AI & API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/highway_pilot

# JWT
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis
REDIS_URL=redis://localhost:6379

# Vector DB
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=production

# AI Model Selection
AI_MODEL_PRIMARY=openai
AI_MODEL_FALLBACK=anthropic
ROUTE_OPTIMIZATION_MODEL=openai
DISPATCH_MODEL=openai
ANALYTICS_MODEL=claude

# CORS
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

---

## 🧪 Testing

### Test Route Optimization
```bash
curl -X POST http://localhost:8000/api/ai/optimize-route \
  -H "Content-Type: application/json" \
  -d '{
    "stops": [
      {
        "job_id": "JOB-001",
        "location": {"lat": 40.7128, "lng": -74.0060, "address": "New York"},
        "priority": 5
      }
    ],
    "vehicle_type": "standard"
  }'
```

### Test Auto-Dispatch
```bash
curl -X POST http://localhost:8000/api/ai/auto-dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "job": {
      "id": "JOB-001",
      "pickup_location": {"lat": 40.7128, "lng": -74.0060},
      "delivery_location": {"lat": 34.0522, "lng": -118.2437},
      "weight": 1000,
      "cargo_type": "general",
      "priority": 8
    },
    "available_drivers": [
      {
        "id": "DRV-001",
        "name": "John Smith",
        "current_location": {"lat": 40.7128, "lng": -74.0060},
        "available_capacity": 5000,
        "rating": 4.8
      }
    ]
  }'
```

---

## 📊 Performance Optimization

### AI Model Selection
- **OpenAI GPT-4** - Best for complex reasoning (route optimization, dispatch)
- **Claude** - Excellent for detailed analysis (driver analytics)
- **GPT-3.5-turbo** - Fast and cost-effective for straightforward tasks

### Caching Strategy
- Route cache: 1 hour
- Driver analytics: 24 hours
- Maintenance predictions: 7 days
- Demand forecasts: 3 days

### Database Optimization
- Index on driver_id, job_id, vehicle_id
- Partition large tables by date
- Archive old records (> 2 years)

---

## 🚀 Deployment

### Docker Deployment
```bash
# Build backend image
docker build -t highway-pilot-backend ./backend

# Build frontend image
docker build -t highway-pilot-frontend ./pilot-web

# Run with docker-compose
docker-compose up
```

### Production Checklist
- [ ] Set strong SECRET_KEY in production .env
- [ ] Configure SSL/HTTPS
- [ ] Set up database backups
- [ ] Configure Redis persistence
- [ ] Set up monitoring and logging
- [ ] Configure CDN for frontend assets
- [ ] Enable rate limiting on API endpoints
- [ ] Set up API authentication (JWT tokens)
- [ ] Configure CORS properly
- [ ] Test all AI features with production models

---

## 🔐 Security

### API Security
- JWT token-based authentication
- CORS headers properly configured
- Rate limiting on all endpoints
- Input validation on all requests
- SQL injection prevention via ORM

### Data Protection
- Encrypted connections (SSL/TLS)
- Password hashing with bcrypt
- Sensitive data in environment variables
- Database encryption at rest

---

## 📞 Support & Documentation

- **Architecture**: See `docs/ARCHITECTURE.md`
- **Roadmap**: See `docs/ROADMAP.md`
- **Vision**: See `docs/VISION.md`

---

## 🎯 Next Steps

1. ✅ **Backend** - Set up and test AI services
2. ✅ **Frontend** - Build user interface components
3. ⏳ **Integration** - Connect all components
4. ⏳ **Testing** - Comprehensive testing
5. ⏳ **Deployment** - Production deployment
6. ⏳ **Monitoring** - Set up observability
7. ⏳ **Optimization** - Fine-tune AI models

---

## 📝 License

This project is proprietary software. All rights reserved.

---

**Highway Pilot** - Where AI drives logistics forward! 🛣️🤖
