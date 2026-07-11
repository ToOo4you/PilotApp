# 🛣️ Highway Pilot - Developer Guide

## Overview

Highway Pilot is a modular AI-powered logistics platform. This guide explains how to work with the system.

---

## 🏗️ Architecture Overview

```
User Interface (React)
        ↓
API Routes (FastAPI)
        ↓
Service Layer (AI Services)
        ↓
External AI APIs (OpenAI/Claude)
        ↓
Database & Cache (PostgreSQL/Redis)
```

---

## 📦 Core Components

### 1. AI Service Layer (`backend/services/`)

Each service is a self-contained module with specific responsibility:

```python
# Pattern: All services follow async/await and return dataclasses

from services.ai_service import ai_service  # Core AI provider
from services.route_optimizer import route_optimizer
from services.dispatch_service import dispatch_service
from services.maintenance_service import maintenance_service
from services.driver_analytics import driver_analytics
from services.forecasting_service import forecasting_service
from services.chatbot_service import chatbot
```

### 2. API Routes (`backend/routes/ai_routes.py`)

All AI features exposed as REST endpoints:

```python
@router.post("/api/ai/optimize-route")
async def optimize_route(...):
    # Calls route_optimizer service
    # Returns: Optimized route with metrics

@router.post("/api/ai/auto-dispatch")
async def auto_dispatch_job(...):
    # Calls dispatch_service
    # Returns: Job assignment with confidence

# etc...
```

### 3. Frontend Components (`pilot-web/src/components/`)

React components for each AI feature:

```jsx
<AIChat />                    // Chat interface
<RouteOptimizer />           // Route planning
<DispatchDashboard />        // Job assignment
<DriverAnalytics />          // Performance analysis
<MaintenancePredictor />     // Vehicle health
```

---

## 🔄 Data Flow Example: Route Optimization

### Step-by-step flow:

1. **User Input** (React)
   ```jsx
   // User adds stops and clicks "Optimize"
   <RouteOptimizer />
   ```

2. **API Call**
   ```javascript
   fetch('POST /api/ai/optimize-route', {stops, vehicle_type, ...})
   ```

3. **Backend Processing**
   ```python
   @router.post("/api/ai/optimize-route")
   async def optimize_route(stops, vehicle_type, ...):
       # Convert DTOs to service objects
       route_stops = [RouteStop(...) for stop in stops]
       
       # Call service
       optimized = await route_optimizer.optimize_route(
           route_stops,
           vehicle_type,
           ...
       )
       
       return optimized
   ```

4. **AI Service**
   ```python
   class RouteOptimizationService:
       async def optimize_route(self, stops, vehicle_type, ...):
           # Build AI prompt
           prompt = f"Optimize this route: {stops}"
           
           # Call AI model
           response = await ai_service.call_ai(
               prompt,
               model="gpt-4",
               temperature=0.3
           )
           
           # Parse and return
           return OptimizedRoute(...)
   ```

5. **AI Model** (OpenAI)
   - Receives detailed prompt with route information
   - Analyzes traffic, distance, priorities
   - Returns optimized order with reasoning

6. **Response Back**
   ```json
   {
     "status": "success",
     "route": {
       "stops": [optimized_order],
       "total_distance": 45.2,
       "estimated_duration_minutes": 120,
       "confidence_score": 0.92
     }
   }
   ```

7. **Display** (React)
   ```jsx
   // Display results in RouteOptimizer component
   ```

---

## 🧠 How AI Integration Works

### Multi-Model Strategy

```python
# backend/services/ai_service.py

class AIServiceManager:
    def get_provider(self, provider_name=None):
        if provider_name == "claude":
            return self.claude_provider  # Anthropic
        return self.openai_provider      # OpenAI
    
    async def call_ai(self, prompt, provider=None, **kwargs):
        try:
            prov = self.get_provider(provider)
            return await prov.call(prompt, **kwargs)
        except Exception as e:
            # Automatic fallback
            fallback = "claude" if self.primary == "openai" else "openai"
            return await self.get_provider(fallback).call(...)
```

### Configuration

```env
# backend/.env
AI_MODEL_PRIMARY=openai              # Use GPT-4 first
AI_MODEL_FALLBACK=anthropic          # Fall back to Claude

# Route-specific models
ROUTE_OPTIMIZATION_MODEL=openai      # GPT-4 for routing
DISPATCH_MODEL=openai                # GPT-4 for dispatch
ANALYTICS_MODEL=claude               # Claude for detailed analysis
FORECASTING_MODEL=openai             # GPT-4 for forecasting
```

---

## 🚀 Adding a New AI Feature

### Example: Add "Fuel Efficiency Optimizer"

#### 1. Create Service (`backend/services/fuel_optimizer.py`)

```python
class FuelOptimizationService:
    async def optimize_fuel_consumption(self, vehicle_data, route_data):
        prompt = f"""
        Analyze this vehicle and route to optimize fuel consumption.
        Vehicle: {vehicle_data}
        Route: {route_data}
        
        Provide: fuel_savings_percentage, recommended_speed, stops_to_add
        """
        
        response = await ai_service.call_ai(prompt, model="gpt-4")
        return json.loads(response)

fuel_optimizer = FuelOptimizationService()
```

#### 2. Add API Route (`backend/routes/ai_routes.py`)

```python
@router.post("/api/ai/optimize-fuel")
async def optimize_fuel(vehicle_data, route_data):
    try:
        result = await fuel_optimizer.optimize_fuel_consumption(
            vehicle_data,
            route_data
        )
        return {"status": "success", "optimization": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### 3. Add Frontend Component (`pilot-web/src/components/FuelOptimizer.jsx`)

```jsx
import React, { useState } from 'react';

const FuelOptimizer = () => {
    const [result, setResult] = useState(null);
    
    const optimize = async (vehicleData, routeData) => {
        const response = await fetch('/api/ai/optimize-fuel', {
            method: 'POST',
            body: JSON.stringify({ vehicleData, routeData })
        });
        const data = await response.json();
        setResult(data.optimization);
    };
    
    return (
        <div className="fuel-optimizer">
            {/* UI here */}
        </div>
    );
};

export default FuelOptimizer;
```

#### 4. Add to App Navigation

```jsx
// pilot-web/src/App.jsx
import FuelOptimizer from './components/FuelOptimizer';

// In button group
<button onClick={() => setPage('Fuel')}>⛽ Fuel Optimizer</button>

// In routing
{page === 'Fuel' && <FuelOptimizer />}
```

---

## 🧪 Testing

### Test Backend Service Directly

```bash
curl -X POST http://localhost:8000/api/ai/optimize-route \
  -H "Content-Type: application/json" \
  -d '{"stops": [...], "vehicle_type": "truck"}'
```

### Test AI Model Response

```python
# In Python REPL
from services.route_optimizer import route_optimizer
result = await route_optimizer.optimize_route(stops, "standard")
print(result)
```

### Test Frontend Component

```bash
cd pilot-web
npm run dev
# Navigate to component in browser
```

---

## 🔐 Security Best Practices

### Environment Variables
```python
# ✅ GOOD
api_key = os.getenv("OPENAI_API_KEY")

# ❌ WRONG - Never hardcode!
api_key = "sk-..."
```

### Input Validation
```python
# ✅ Always validate inputs
from pydantic import BaseModel, Field

class LocationInput(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
```

### Error Handling
```python
# ✅ Catch and log errors
try:
    result = await service.do_something()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=500, detail="Internal error")
```

---

## 📊 Performance Tips

### Caching
```python
# Use Redis for frequently accessed data
cache_key = f"route_optimization:{stops_hash}"
cached = redis_client.get(cache_key)
if cached:
    return json.loads(cached)
```

### Async/Await
```python
# ✅ Use async for I/O operations
async def process_jobs(jobs):
    tasks = [dispatch_service.assign_job(job) for job in jobs]
    return await asyncio.gather(*tasks)
```

### Batch Processing
```python
# ✅ Process multiple items together
assignments = await dispatch_service.assign_batch_jobs(
    jobs=[...],
    drivers=[...],
    strategy="balanced"
)
```

---

## 📚 Documentation

### Docstring Format

```python
async def optimize_route(
    self,
    stops: List[RouteStop],
    vehicle_type: str = "standard"
) -> OptimizedRoute:
    """
    Optimize delivery route using AI.
    
    Args:
        stops: List of delivery stops to optimize
        vehicle_type: Type of vehicle (standard, van, truck, hazmat)
    
    Returns:
        OptimizedRoute with optimized stops and metrics
    
    Raises:
        ValueError: If less than 2 stops provided
        RuntimeError: If AI call fails
    
    Example:
        >>> result = await optimizer.optimize_route(stops, "truck")
        >>> print(result.total_distance)
    """
```

---

## 🐛 Debugging

### Enable Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Processing stops: {stops}")
logger.info(f"Optimization complete: {result}")
logger.error(f"AI call failed: {error}")
```

### Check API Responses

```python
# Print raw AI response
response_text = await ai_service.call_ai(prompt)
print("Raw AI response:")
print(response_text)
```

### Test with Print Statements

```python
async def optimize_route(self, stops, vehicle_type):
    print(f"[DEBUG] Input stops: {stops}")
    
    prompt = f"..."
    print(f"[DEBUG] Prompt: {prompt[:100]}...")  # First 100 chars
    
    response = await ai_service.call_ai(prompt)
    print(f"[DEBUG] AI Response: {response[:200]}...")  # First 200 chars
    
    result = OptimizedRoute(...)
    print(f"[DEBUG] Result: {result}")
    return result
```

---

## 📝 Commit Guidelines

When adding features:

```bash
git add .
git commit -m "feat: Add fuel optimizer service

- Add FuelOptimizationService with consumption analysis
- Add /api/ai/optimize-fuel endpoint
- Add FuelOptimizer React component
- Update App.jsx with new feature

Closes #123"
```

---

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **Pydantic**: https://docs.pydantic.dev/
- **React Hooks**: https://react.dev/reference/react
- **OpenAI API**: https://platform.openai.com/docs/
- **Anthropic Claude**: https://www.anthropic.com/api

---

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/new-feature`
2. Add tests for your changes
3. Update documentation
4. Submit PR with description

---

## ❓ FAQ

**Q: Can I use a different AI model?**
A: Yes! Edit `backend/.env` and choose from `openai` or `anthropic`

**Q: How do I add database models?**
A: Add to `backend/database/models.py` and run migrations

**Q: Can I customize AI prompts?**
A: Yes! Each service has customizable prompts in their methods

**Q: What if OpenAI API is down?**
A: System automatically switches to Anthropic (configured fallback)

---

## 📞 Support

For issues or questions, refer to:
- `HIGHWAY_PILOT_SETUP.md` - Setup guide
- `README_HIGHWAY_PILOT.md` - Feature overview
- Individual service docstrings

---

**Happy coding! 🚀**
