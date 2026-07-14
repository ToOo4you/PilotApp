"""
AI Service Layer - Core AI-powered logistics functions
"""
import json
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from abc import ABC, abstractmethod

try:
    import openai
except Exception:
    openai = None

try:
    from anthropic import Anthropic
except Exception:
    Anthropic = None

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Base class for AI providers"""
    
    @abstractmethod
    async def call(self, prompt: str, **kwargs) -> str:
        """Make an AI call and return response"""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")
        openai.api_key = self.api_key
        self.client = openai.OpenAI(api_key=self.api_key)
    
    async def call(self, prompt: str, model: str = None, temperature: float = 0.7, **kwargs) -> str:
        """Call OpenAI API"""
        try:
            model_name = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class ClaudeProvider(AIProvider):
    """Anthropic Claude API integration"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not configured")
        self.client = Anthropic(api_key=self.api_key)
    
    async def call(self, prompt: str, model: str = None, **kwargs) -> str:
        """Call Claude API"""
        try:
            model_name = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
            response = self.client.messages.create(
                model=model_name,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise


class AIServiceManager:
    """Central manager for AI services"""
    
    def __init__(self):
        self.openai_provider = None
        self.claude_provider = None

        if openai is not None:
            try:
                self.openai_provider = OpenAIProvider()
            except Exception as exc:
                logger.warning("OpenAI provider unavailable: %s", exc)

        if Anthropic is not None:
            try:
                self.claude_provider = ClaudeProvider()
            except Exception as exc:
                logger.warning("Anthropic provider unavailable: %s", exc)

        self.primary_provider = os.getenv("AI_MODEL_PRIMARY", "openai")
        default_mock = "false" if os.getenv("APP_ENV", "development").lower() == "production" else "true"
        self.mock_mode = os.getenv("AI_MOCK_MODE", default_mock).lower() == "true"

        # Auto-enable mock responses when no provider is configured so AI endpoints still function.
        if self.openai_provider is None and self.claude_provider is None and not self.mock_mode:
            logger.warning("No AI providers available; enabling mock mode fallback")
            self.mock_mode = True

    def _normalize_model_for_provider(self, model: Optional[str], provider_name: str) -> Optional[str]:
        """Map legacy/unsupported model names to safer defaults by provider."""
        if not model:
            return None

        if provider_name == "openai":
            aliases = {
                "gpt-4": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                "gpt-3.5-turbo": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            }
            return aliases.get(model, model)

        if provider_name == "claude":
            aliases = {
                "claude-3-opus-20240229": os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            }
            return aliases.get(model, model)

        return model
    
    def get_provider(self, provider_name: str = None) -> AIProvider:
        """Get AI provider by name"""
        provider = provider_name or self.primary_provider
        if provider == "claude":
            if self.claude_provider is not None:
                return self.claude_provider
            # fall back to openai if available
            if self.openai_provider is not None:
                return self.openai_provider
            raise RuntimeError("No AI provider available (install anthropic or openai)")

        # default to openai
        if self.openai_provider is not None:
            return self.openai_provider
        if self.claude_provider is not None:
            return self.claude_provider
        raise RuntimeError("No AI provider available (install openai or anthropic)")
    
    async def call_ai(self, prompt: str, provider: str = None, **kwargs) -> str:
        """Call AI with fallback support"""
        requested_provider = provider or self.primary_provider
        requested_model = kwargs.get("model")
        kwargs["model"] = self._normalize_model_for_provider(requested_model, requested_provider)

        try:
            prov = self.get_provider(provider)
            return await prov.call(prompt, **kwargs)
        except Exception as e:
            logger.warning(f"Primary provider failed: {e}. Trying fallback...")
            # attempt fallback provider if available
            fallback = "claude" if requested_provider == "openai" else "openai"
            try:
                fallback_prov = self.get_provider(fallback)
                kwargs["model"] = self._normalize_model_for_provider(requested_model, fallback)
                return await fallback_prov.call(prompt, **kwargs)
            except Exception:
                if self.mock_mode:
                    logger.warning("AI providers unavailable, using mock mode response")
                    return self._mock_response(prompt)
                raise

    def get_health_status(self) -> Dict[str, Any]:
        """Expose runtime provider status for diagnostics/health endpoints."""
        active_provider = None
        if self.openai_provider is not None:
            active_provider = "openai"
        elif self.claude_provider is not None:
            active_provider = "claude"

        return {
            "primary_provider": self.primary_provider,
            "active_provider": active_provider,
            "openai_configured": self.openai_provider is not None,
            "anthropic_configured": self.claude_provider is not None,
            "mock_mode": self.mock_mode,
        }

    def _mock_response(self, prompt: str) -> str:
        """Return deterministic JSON/text mock responses for local/staging without provider keys."""
        lower_prompt = prompt.lower()

        if "format response as json with keys: order" in lower_prompt or "optimize this delivery route" in lower_prompt:
            match = re.search(r"optimal stop order \(1 to (\d+)\)", lower_prompt)
            stop_count = int(match.group(1)) if match else 2
            return json.dumps(
                {
                    "order": list(range(1, stop_count + 1)),
                    "distances": [42.0] * max(1, stop_count - 1),
                    "total_distance": float(42 * max(1, stop_count - 1)),
                    "duration": int(55 * max(1, stop_count - 1)),
                    "confidence": 88,
                    "traffic_notes": "Moderate congestion on urban connectors.",
                    "recommendations": "Depart 20 minutes earlier to reduce peak traffic impact.",
                }
            )

        if "predict updated etas" in lower_prompt:
            return json.dumps(
                {
                    "updated_total_duration": 145,
                    "arrival_time": "16:10",
                    "confidence": 82,
                    "potential_delays": ["Short delay near interchange"]
                }
            )

        if "detect potential delays" in lower_prompt:
            return json.dumps(
                {
                    "potential_delays": ["Weather slowdown likely in 45 minutes"],
                    "recommended_actions": ["Re-route via secondary corridor"],
                    "priority_adjustments": ["Prioritize stop 1 and 3"]
                }
            )

        if "autonomously assign this job" in lower_prompt:
            driver_match = re.search(r"id: ([a-z0-9\-_]+)", lower_prompt)
            driver_id = driver_match.group(1).upper() if driver_match else "D-1001"
            return json.dumps(
                {
                    "driver_id": driver_id,
                    "driver_name": "Mock Driver",
                    "confidence_score": 86,
                    "reason": "Best match based on capacity, proximity, and current workload.",
                    "pickup_eta": "14:20",
                    "delivery_eta": "16:00",
                    "optimization_notes": "Balanced assignment with low risk of delay.",
                }
            )

        if "perform batch dispatch assignment" in lower_prompt:
            job_ids = re.findall(r"job\s+([a-z0-9\-_]+)", lower_prompt)
            if not job_ids:
                job_ids = ["JOB-001", "JOB-002"]
            assignments = [
                {
                    "job_id": job_id.upper(),
                    "driver_id": "D-1001",
                    "confidence": 80,
                    "reason": "Closest available qualified driver.",
                }
                for job_id in job_ids
            ]
            return json.dumps(assignments)

        if "predict maintenance needs" in lower_prompt:
            return json.dumps(
                [
                    {
                        "predicted_issue": "Front tire wear imbalance",
                        "urgency_level": "medium",
                        "estimated_days_to_failure": 18,
                        "recommended_action": "Rotate and align tires; inspect suspension.",
                        "estimated_cost": 380,
                        "confidence_score": 84,
                        "parts_needed": ["Tire set (front)", "Alignment kit"],
                        "downtime_estimate_hours": 2.5,
                    }
                ]
            )

        if "analyze driver performance" in lower_prompt:
            return json.dumps(
                {
                    "performance_level": "good",
                    "safety_score": 89,
                    "efficiency_score": 85,
                    "customer_service_score": 91,
                    "key_strengths": ["On-time deliveries", "Strong customer feedback"],
                    "areas_for_improvement": ["Reduce harsh braking events"],
                    "coaching_suggestions": ["Defensive driving refresher"],
                    "risk_factors": ["Mild fatigue pattern on late shifts"],
                    "retention_risk": 24,
                    "general_recommendations": ["Schedule monthly coaching check-in"],
                }
            )

        if "forecast shipping demand" in lower_prompt:
            return json.dumps(
                {
                    "predicted_volume": 1420,
                    "confidence_interval": 86,
                    "growth_rate": 6.2,
                    "seasonal_factors": {"Mon": 1.02, "Tue": 1.05, "Wed": 1.07, "Thu": 1.03, "Fri": 0.97},
                    "recommended_capacity": 1580,
                    "peak_days": ["Tuesday", "Wednesday"],
                    "supply_recommendations": ["Add one extra day-shift truck Tue/Wed"],
                    "risk_factors": ["Fuel price volatility", "Port congestion"],
                }
            )

        if "respond with json containing:" in lower_prompt and "followup_questions" in lower_prompt:
            return json.dumps(
                {
                    "message": "Recommended action: assign highest-rated nearby driver and pre-stage backup for peak traffic window.",
                    "action_type": "dispatch_suggestion",
                    "action_data": {"priority": "high", "strategy": "proximity_and_capacity"},
                    "context": "dispatch",
                    "confidence_score": 82,
                    "followup_questions": [
                        "Do you want me to optimize the route after assignment?",
                        "Should I include a backup driver recommendation?",
                    ],
                }
            )

        if "provide as json array of strings" in lower_prompt:
            return json.dumps(
                [
                    "Review top-priority jobs for the next 2 hours",
                    "Run route optimization for active deliveries",
                    "Check HOS summary for drivers nearing limits",
                ]
            )

        if "which interpretation is most likely" in lower_prompt:
            return json.dumps(
                {
                    "interpretation_index": 1,
                    "explanation": "First interpretation aligns most closely with dispatch intent and recent conversation context.",
                }
            )

        return "Mock response: no provider configured and no specialized template matched this prompt."


# Global AI service manager
ai_service = AIServiceManager()
