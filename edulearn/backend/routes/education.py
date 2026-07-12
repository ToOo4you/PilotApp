"""
EduLearn AI — Education API Routes
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from edulearn.backend.services.education_service import (
    LearnerProfile,
    education_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/education", tags=["Education"])


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class ProfileData(BaseModel):
    learner_id: str = "guest"
    name: str = "Learner"
    age: int = 10
    grade_level: str = "4th"
    primary_needs: List[str] = Field(default_factory=list)
    learning_style: str = "visual"
    interests: List[str] = Field(default_factory=list)
    communication_style: str = "verbal"
    sensory_preferences: Dict[str, Any] = Field(default_factory=dict)
    skill_levels: Dict[str, str] = Field(default_factory=dict)
    strengths: List[str] = Field(default_factory=list)
    challenges: List[str] = Field(default_factory=list)


class LessonRequest(BaseModel):
    learner_profile: ProfileData
    subject: str
    topic: str
    duration_minutes: int = 20
    lesson_format: str = "visual"


class TutorChatRequest(BaseModel):
    learner_profile: ProfileData
    message: str
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    current_subject: Optional[str] = None


class QuizRequest(BaseModel):
    learner_profile: ProfileData
    subject: str
    topic: str
    question_count: int = 4


class ProgressRequest(BaseModel):
    learner_profile: ProfileData
    session_data: Dict[str, Any]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _to_profile(data: ProfileData) -> LearnerProfile:
    return LearnerProfile(
        learner_id=data.learner_id,
        name=data.name,
        age=data.age,
        grade_level=data.grade_level,
        primary_needs=data.primary_needs,
        learning_style=data.learning_style,
        interests=data.interests,
        communication_style=data.communication_style,
        sensory_preferences=data.sensory_preferences,
        skill_levels=data.skill_levels,
        strengths=data.strengths,
        challenges=data.challenges,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/lesson/generate")
async def generate_lesson(req: LessonRequest):
    """Generate a fully personalised AI lesson."""
    try:
        lesson = await education_service.generate_lesson(
            _to_profile(req.learner_profile),
            req.subject,
            req.topic,
            req.duration_minutes,
            req.lesson_format,
        )
        return {
            "status": "success",
            "lesson": {
                "title": lesson.title,
                "subject": lesson.subject,
                "topic": lesson.topic,
                "grade_level": lesson.grade_level,
                "objectives": lesson.objectives,
                "introduction": lesson.introduction,
                "activities": lesson.activities,
                "key_vocabulary": lesson.key_vocabulary,
                "summary": lesson.summary,
                "break_reminders": lesson.break_reminders,
                "visual_cues": lesson.visual_cues,
                "extension_activities": lesson.extension_activities,
                "accommodation_notes": lesson.accommodation_notes,
            },
        }
    except Exception as exc:
        logger.error("generate_lesson endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/tutor/chat")
async def tutor_chat(req: TutorChatRequest):
    """Chat with the AI tutor."""
    try:
        resp = await education_service.tutor_chat(
            _to_profile(req.learner_profile),
            req.message,
            req.conversation_history,
            req.current_subject,
        )
        return {
            "status": "success",
            "response": {
                "message": resp.message,
                "tone": resp.tone,
                "visual_support": resp.visual_support,
                "next_step": resp.next_step,
                "break_suggested": resp.break_suggested,
                "confidence_level": resp.confidence_level,
            },
        }
    except Exception as exc:
        logger.error("tutor_chat endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/quiz/generate")
async def generate_quiz(req: QuizRequest):
    """Generate a personalised adaptive quiz."""
    try:
        questions = await education_service.generate_quiz(
            _to_profile(req.learner_profile),
            req.subject,
            req.topic,
            req.question_count,
        )
        return {
            "status": "success",
            "quiz": [
                {
                    "question": q.question,
                    "question_type": q.question_type,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "hint": q.hint,
                    "image_description": q.image_description,
                }
                for q in questions
            ],
        }
    except Exception as exc:
        logger.error("generate_quiz endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/progress/analyze")
async def analyze_progress(req: ProgressRequest):
    """Analyse learner progress and return AI insights."""
    try:
        insight = await education_service.analyze_progress(
            _to_profile(req.learner_profile),
            req.session_data,
        )
        return {
            "status": "success",
            "insight": {
                "overall_progress": insight.overall_progress,
                "strengths_identified": insight.strengths_identified,
                "areas_for_focus": insight.areas_for_focus,
                "recommended_next_topics": insight.recommended_next_topics,
                "engagement_level": insight.engagement_level,
                "suggested_modifications": insight.suggested_modifications,
                "celebration_message": insight.celebration_message,
                "parent_notes": insight.parent_notes,
            },
        }
    except Exception as exc:
        logger.error("analyze_progress endpoint error: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "EduLearn AI Education Platform",
        "timestamp": datetime.now().isoformat(),
        "features": ["lesson_generation", "ai_tutor", "adaptive_quiz", "progress_analysis"],
    }
