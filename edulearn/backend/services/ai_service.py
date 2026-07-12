"""
EduLearn AI - Core AI service layer
Supports OpenAI and Anthropic with mock fallback
"""
import json
import logging
import os
import re
import asyncio
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import openai as _openai_mod
except Exception:
    _openai_mod = None

try:
    from anthropic import Anthropic as _Anthropic
except Exception:
    _Anthropic = None


class _AIProvider(ABC):
    @abstractmethod
    async def call(self, prompt: str, **kwargs) -> str:
        pass


class _OpenAIProvider(_AIProvider):
    def __init__(self, api_key: str):
        self._client = _openai_mod.OpenAI(api_key=api_key)

    async def call(self, prompt: str, model: str = "gpt-4", temperature: float = 0.7, **kwargs) -> str:
        resp = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return resp.choices[0].message.content


class _ClaudeProvider(_AIProvider):
    def __init__(self, api_key: str):
        self._client = _Anthropic(api_key=api_key)

    async def call(self, prompt: str, model: str = "claude-3-opus-20240229", **kwargs) -> str:
        resp = await asyncio.to_thread(
            self._client.messages.create,
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text


class AIService:
    """Central AI service with provider fallback and mock mode."""

    def __init__(self):
        self._openai: Optional[_AIProvider] = None
        self._claude: Optional[_AIProvider] = None

        if _openai_mod is not None:
            key = os.getenv("OPENAI_API_KEY", "")
            if key:
                try:
                    self._openai = _OpenAIProvider(key)
                except Exception as exc:
                    logger.warning("OpenAI init failed: %s", exc)

        if _Anthropic is not None:
            key = os.getenv("ANTHROPIC_API_KEY", "")
            if key:
                try:
                    self._claude = _ClaudeProvider(key)
                except Exception as exc:
                    logger.warning("Anthropic init failed: %s", exc)

        self._primary = os.getenv("AI_MODEL_PRIMARY", "openai")
        default_mock = "true" if os.getenv("APP_ENV", "development").lower() != "production" else "false"
        self.mock_mode = os.getenv("AI_MOCK_MODE", default_mock).lower() == "true"

    def _get_provider(self) -> Optional[_AIProvider]:
        if self._primary == "claude":
            return self._claude or self._openai
        return self._openai or self._claude

    async def call(self, prompt: str, **kwargs) -> str:
        provider = self._get_provider()
        if provider is not None:
            try:
                return await provider.call(prompt, **kwargs)
            except Exception as exc:
                logger.warning("Primary AI provider failed: %s — trying fallback", exc)
                fallback = self._claude if self._primary == "openai" else self._openai
                if fallback is not None:
                    try:
                        return await fallback.call(prompt, **kwargs)
                    except Exception as exc2:
                        logger.warning("Fallback AI provider also failed: %s", exc2)

        if self.mock_mode:
            return self._mock(prompt)
        raise RuntimeError("No AI provider available and mock mode is disabled.")

    # ------------------------------------------------------------------
    # Mock responses — deterministic JSON stubs used when no key is set
    # ------------------------------------------------------------------
    def _mock(self, prompt: str) -> str:
        p = prompt.lower()

        if "generate_lesson" in p or "personalized lesson" in p:
            topic_m = re.search(r'topic["\s:]+([^\n"]+)', prompt)
            topic = topic_m.group(1).strip() if topic_m else "the topic"
            return json.dumps({
                "title": f"Exploring {topic} Your Way! 🌟",
                "objectives": [
                    f"Understand what {topic} is",
                    f"Connect {topic} to your interests",
                    f"Practice one skill about {topic}",
                ],
                "introduction": (
                    f"Hey, welcome! Today we're going to explore {topic}. "
                    "We will go step by step — no rush, no pressure. "
                    "You've got this! 🎉"
                ),
                "activities": [
                    {"name": "Warm-Up", "description": "Look at a picture and share one thought.", "duration_minutes": 3, "type": "visual"},
                    {"name": "Main Lesson", "description": f"We learn about {topic} using pictures and short sentences.", "duration_minutes": 10, "type": "visual"},
                    {"name": "Practice", "description": "Try 2–3 simple examples at your own pace.", "duration_minutes": 5, "type": "hands_on"},
                    {"name": "Wrap-Up", "description": "Share one thing you learned today! Great work!", "duration_minutes": 2, "type": "discussion"},
                ],
                "key_vocabulary": [
                    {"word": topic, "definition": "The big idea we are learning today.", "example": f"Today I learned about {topic}!"},
                ],
                "summary": f"You explored {topic} today. Every step you take is amazing progress. Well done! 🌈",
                "break_reminders": ["Stretch break after the main lesson", "Deep breath if feeling overwhelmed"],
                "visual_cues": ["Draw a quick picture", "Use your fingers to count steps"],
                "extension_activities": [f"Tell someone at home one fact about {topic}!"],
                "accommodation_notes": "Content structured with short steps, visual cues, and positive reinforcement.",
            })

        if "tutor_chat" in p or "ai tutor" in p:
            return json.dumps({
                "message": "Great question! Let's figure this out together, one small step at a time. You're doing awesome just by asking! 😊",
                "tone": "encouraging",
                "visual_support": None,
                "next_step": "Let's try one example together first.",
                "break_suggested": False,
                "confidence_level": 0.9,
            })

        if "generate_quiz" in p or "quiz" in p:
            return json.dumps([
                {
                    "question": "What is the main idea of today's lesson?",
                    "question_type": "multiple_choice",
                    "options": ["A. The topic we studied", "B. Something else", "C. I'm not sure", "D. Everything!"],
                    "correct_answer": "A. The topic we studied",
                    "hint": "Think about what we talked about first!",
                    "image_description": None,
                },
                {
                    "question": "Learning new things can be fun. True or False?",
                    "question_type": "true_false",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "hint": "What do you think?",
                    "image_description": None,
                },
                {
                    "question": "It is OK to ask for help when something is hard.",
                    "question_type": "true_false",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "hint": "Everyone needs help sometimes!",
                    "image_description": None,
                },
            ])

        if "analyze_progress" in p or "progress" in p:
            return json.dumps({
                "overall_progress": "good",
                "strengths_identified": ["Shows up and tries hard", "Asks thoughtful questions", "Stays engaged"],
                "areas_for_focus": ["Continue building on today's concepts"],
                "recommended_next_topics": ["Next step in current subject", "Review key vocabulary"],
                "engagement_level": "high",
                "suggested_modifications": ["Short breaks every 10 minutes", "Use visuals alongside text"],
                "celebration_message": "You worked so hard today and it absolutely shows! Every lesson is a win. Keep going — you are incredible! 🌟🎉",
                "parent_notes": "Great session today! Celebrate your child's effort and curiosity. They are making real progress!",
            })

        return json.dumps({"message": "Mock response — no provider configured.", "status": "mock"})


ai_service = AIService()
