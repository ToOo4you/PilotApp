"""
EduLearn AI — Education Service
Personalized AI-driven learning for autism, ADHD, dyslexia, and other learning differences.
"""
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from edulearn.backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Domain models
# ---------------------------------------------------------------------------

@dataclass
class LearnerProfile:
    learner_id: str
    name: str
    age: int = 10
    grade_level: str = "4th"
    # e.g. ["autism", "adhd", "dyslexia", "dyscalculia", "sensory_processing"]
    primary_needs: List[str] = field(default_factory=list)
    # "visual" | "auditory" | "kinesthetic" | "reading_writing"
    learning_style: str = "visual"
    interests: List[str] = field(default_factory=list)
    # "verbal" | "AAC" | "written" | "visual_symbols"
    communication_style: str = "verbal"
    sensory_preferences: Dict[str, Any] = field(default_factory=dict)
    # subject -> skill level string, e.g. {"math": "grade_2"}
    skill_levels: Dict[str, str] = field(default_factory=dict)
    strengths: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)


@dataclass
class LessonContent:
    title: str
    subject: str
    topic: str
    grade_level: str
    objectives: List[str]
    introduction: str
    activities: List[Dict[str, Any]]
    key_vocabulary: List[Dict[str, str]]
    summary: str
    break_reminders: List[str]
    visual_cues: List[str]
    extension_activities: List[str]
    accommodation_notes: str


@dataclass
class TutorResponse:
    message: str
    tone: str  # encouraging | celebratory | calm | patient
    visual_support: Optional[str]
    next_step: str
    break_suggested: bool
    confidence_level: float


@dataclass
class QuizQuestion:
    question: str
    question_type: str  # multiple_choice | true_false | fill_blank
    options: List[str]
    correct_answer: str
    hint: str
    image_description: Optional[str]


@dataclass
class ProgressInsight:
    overall_progress: str  # excellent | good | growing | needs_support
    strengths_identified: List[str]
    areas_for_focus: List[str]
    recommended_next_topics: List[str]
    engagement_level: str  # high | medium | low
    suggested_modifications: List[str]
    celebration_message: str
    parent_notes: str


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class EducationService:
    """AI-powered personalized education service for diverse learners."""

    # -- helpers ------------------------------------------------------------

    def _learner_context(self, p: LearnerProfile) -> str:
        needs = ", ".join(p.primary_needs) if p.primary_needs else "general learner"
        interests = ", ".join(p.interests) if p.interests else "varied topics"
        return (
            f"Learner: {p.name}, age {p.age}, grade {p.grade_level}. "
            f"Primary needs: {needs}. "
            f"Learning style: {p.learning_style}. "
            f"Interests: {interests}. "
            f"Communication: {p.communication_style}. "
            f"Strengths: {', '.join(p.strengths) if p.strengths else 'being discovered'}. "
            f"Challenges: {', '.join(p.challenges) if p.challenges else 'being identified'}."
        )

    def _accommodation_notes(self, needs: List[str]) -> str:
        notes = []
        if "autism" in needs:
            notes.append("Use predictable structure, explicit instructions, and avoid ambiguous language.")
        if "adhd" in needs:
            notes.append("Keep activities short (5–10 min), add movement breaks, use bold headers.")
        if "dyslexia" in needs:
            notes.append("Use short sentences, larger spacing, avoid dense text blocks.")
        if "dyscalculia" in needs:
            notes.append("Use visual number lines, manipulatives, and real-world examples.")
        if "sensory_processing" in needs:
            notes.append("Reduce visual clutter, offer quiet processing time, avoid sudden changes.")
        return " ".join(notes) if notes else "Adapt pacing and format to learner preferences."

    # -- lesson generation --------------------------------------------------

    async def generate_lesson(
        self,
        profile: LearnerProfile,
        subject: str,
        topic: str,
        duration_minutes: int = 20,
        lesson_format: str = "visual",
    ) -> LessonContent:
        ctx = self._learner_context(profile)
        interests = ", ".join(profile.interests or ["general"])
        needs = ", ".join(profile.primary_needs or ["general"])
        acc = self._accommodation_notes(profile.primary_needs)

        prompt = f"""generate_lesson
You are an expert special-education AI creating a fully personalized lesson.

{ctx}

Create a {duration_minutes}-minute {subject} lesson on "{topic}" using {lesson_format} format.
Weave in the learner's interests ({interests}) throughout the content.
Apply these accommodations for {needs}: {acc}

Rules:
- Short sentences. Simple words.
- Chunked steps — never overwhelming.
- Positive, warm tone throughout.
- Include at least one movement/sensory break suggestion.
- Use emojis sparingly to add warmth.

Respond ONLY with valid JSON:
{{
  "title": "...",
  "objectives": ["..."],
  "introduction": "...",
  "activities": [{{"name":"...","description":"...","duration_minutes":5,"type":"visual|hands_on|discussion|game"}}],
  "key_vocabulary": [{{"word":"...","definition":"...","example":"..."}}],
  "summary": "...",
  "break_reminders": ["..."],
  "visual_cues": ["..."],
  "extension_activities": ["..."],
  "accommodation_notes": "..."
}}"""

        try:
            raw = await ai_service.call(prompt)
            data = json.loads(raw)
            return LessonContent(
                title=data.get("title", topic),
                subject=subject,
                topic=topic,
                grade_level=profile.grade_level,
                objectives=data.get("objectives", []),
                introduction=data.get("introduction", ""),
                activities=data.get("activities", []),
                key_vocabulary=data.get("key_vocabulary", []),
                summary=data.get("summary", ""),
                break_reminders=data.get("break_reminders", []),
                visual_cues=data.get("visual_cues", []),
                extension_activities=data.get("extension_activities", []),
                accommodation_notes=data.get("accommodation_notes", acc),
            )
        except Exception as exc:
            logger.error("generate_lesson failed: %s", exc)
            return self._fallback_lesson(profile, subject, topic, acc)

    def _fallback_lesson(self, profile: LearnerProfile, subject: str, topic: str, acc: str) -> LessonContent:
        interest = (profile.interests or ["your favourite things"])[0]
        name = profile.name
        return LessonContent(
            title=f"Exploring {topic} with {interest}! 🌟",
            subject=subject,
            topic=topic,
            grade_level=profile.grade_level,
            objectives=[
                f"Understand what {topic} is",
                f"Connect {topic} to {interest}",
                "Practice one new skill",
            ],
            introduction=(
                f"Hey {name}! Today we explore {topic}. "
                f"Did you know it connects to {interest}? "
                "Let's go one step at a time — no rush! 😊"
            ),
            activities=[
                {"name": "Warm-Up", "description": f"Think: how might {topic} relate to {interest}? Share one idea!", "duration_minutes": 3, "type": "discussion"},
                {"name": "Main Lesson", "description": f"We learn about {topic} using pictures and short steps.", "duration_minutes": 10, "type": "visual"},
                {"name": "Practice", "description": "Try 2–3 examples. Take your time.", "duration_minutes": 5, "type": "hands_on"},
                {"name": "Wrap-Up", "description": "Tell one thing you learned. Amazing work! 🎉", "duration_minutes": 2, "type": "discussion"},
            ],
            key_vocabulary=[
                {"word": topic, "definition": "The big idea we learned today.", "example": f"Today I learned about {topic}!"},
            ],
            summary=f"You explored {topic} today. Every step is real progress. Well done, {name}! 🌈",
            break_reminders=["Stretch break after Main Lesson", "Deep breaths whenever you need them"],
            visual_cues=["Draw a quick picture of what you learned", "Use fingers to count steps"],
            extension_activities=[f"Tell someone at home one cool fact about {topic}!"],
            accommodation_notes=acc,
        )

    # -- AI tutor chat ------------------------------------------------------

    async def tutor_chat(
        self,
        profile: LearnerProfile,
        message: str,
        conversation_history: List[Dict[str, str]],
        current_subject: Optional[str] = None,
    ) -> TutorResponse:
        ctx = self._learner_context(profile)
        history_str = "\n".join(
            f"{m['role'].title()}: {m['content']}" for m in conversation_history[-6:]
        )
        needs = ", ".join(profile.primary_needs or ["diverse learning needs"])
        interests = ", ".join(profile.interests or ["their interests"])

        prompt = f"""tutor_chat
You are a warm, patient AI tutor supporting students with {needs}.

{ctx}
Subject context: {current_subject or "general learning"}

Recent conversation:
{history_str}

Student says: "{message}"

Tutor guidelines:
- Be encouraging — celebrate every attempt.
- Use simple language; short sentences.
- Connect explanations to interests: {interests}.
- Break down anything complex into tiny steps.
- Suggest a movement break if helpful.
- Never make the student feel bad.

Respond ONLY with valid JSON:
{{
  "message": "...",
  "tone": "encouraging|celebratory|calm|patient",
  "visual_support": null,
  "next_step": "...",
  "break_suggested": false,
  "confidence_level": 0.9
}}"""

        try:
            raw = await ai_service.call(prompt)
            data = json.loads(raw)
            return TutorResponse(
                message=data.get("message", "Great question! Let's figure this out together. 😊"),
                tone=data.get("tone", "encouraging"),
                visual_support=data.get("visual_support"),
                next_step=data.get("next_step", "One small step at a time — you've got this!"),
                break_suggested=bool(data.get("break_suggested", False)),
                confidence_level=float(data.get("confidence_level", 0.9)),
            )
        except Exception as exc:
            logger.error("tutor_chat failed: %s", exc)
            return TutorResponse(
                message=f"Great question, {profile.name}! Let's think about this together. You're doing amazing just by asking! 😊",
                tone="encouraging",
                visual_support=None,
                next_step="Let's try one small step at a time.",
                break_suggested=len(conversation_history) > 10,
                confidence_level=0.9,
            )

    # -- quiz generation ----------------------------------------------------

    async def generate_quiz(
        self,
        profile: LearnerProfile,
        subject: str,
        topic: str,
        question_count: int = 4,
    ) -> List[QuizQuestion]:
        ctx = self._learner_context(profile)
        interests = ", ".join(profile.interests or ["general"])
        needs = ", ".join(profile.primary_needs or ["general"])

        prompt = f"""generate_quiz
Create {question_count} quiz questions on "{topic}" in {subject} for this learner.

{ctx}

Quiz rules:
- Grade-appropriate language for grade {profile.grade_level}.
- Prefer multiple_choice and true_false types.
- One helpful hint per question.
- Connect to learner's interests ({interests}) where natural.
- For {needs}: use concrete, literal wording — no trick questions.
- Tone is warm and encouraging, not a test.

Respond ONLY with a valid JSON array:
[{{
  "question": "...",
  "question_type": "multiple_choice|true_false|fill_blank",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "correct_answer": "A. ...",
  "hint": "...",
  "image_description": null
}}]"""

        try:
            raw = await ai_service.call(prompt)
            data = json.loads(raw)
            return [
                QuizQuestion(
                    question=q.get("question", ""),
                    question_type=q.get("question_type", "multiple_choice"),
                    options=q.get("options", []),
                    correct_answer=q.get("correct_answer", ""),
                    hint=q.get("hint", "Think carefully — you know this!"),
                    image_description=q.get("image_description"),
                )
                for q in data
            ]
        except Exception as exc:
            logger.error("generate_quiz failed: %s", exc)
            return self._fallback_quiz(profile, topic)

    def _fallback_quiz(self, profile: LearnerProfile, topic: str) -> List[QuizQuestion]:
        return [
            QuizQuestion(
                question=f"What is one thing you learned about {topic} today?",
                question_type="multiple_choice",
                options=[f"A. Something about {topic}", "B. Nothing new", "C. I forgot", "D. Everything!"],
                correct_answer=f"A. Something about {topic}",
                hint=f"Think back to our lesson on {topic}!",
                image_description=None,
            ),
            QuizQuestion(
                question=f"Learning about {topic} is fun. True or False?",
                question_type="true_false",
                options=["True", "False"],
                correct_answer="True",
                hint="What do you think? There are no wrong feelings!",
                image_description=None,
            ),
            QuizQuestion(
                question="It is OK to ask for help when something is hard.",
                question_type="true_false",
                options=["True", "False"],
                correct_answer="True",
                hint="Everyone needs help sometimes — that's how we grow!",
                image_description=None,
            ),
        ]

    # -- progress analysis --------------------------------------------------

    async def analyze_progress(
        self,
        profile: LearnerProfile,
        session_data: Dict[str, Any],
    ) -> ProgressInsight:
        ctx = self._learner_context(profile)

        prompt = f"""analyze_progress
Analyze this learner's session and provide warm, supportive insights.

{ctx}

Session data:
{json.dumps(session_data, indent=2)}

Always find something positive first!
Focus on effort, not just accuracy.

Respond ONLY with valid JSON:
{{
  "overall_progress": "excellent|good|growing|needs_support",
  "strengths_identified": ["..."],
  "areas_for_focus": ["..."],
  "recommended_next_topics": ["..."],
  "engagement_level": "high|medium|low",
  "suggested_modifications": ["..."],
  "celebration_message": "...",
  "parent_notes": "..."
}}"""

        try:
            raw = await ai_service.call(prompt)
            data = json.loads(raw)
            return ProgressInsight(
                overall_progress=data.get("overall_progress", "growing"),
                strengths_identified=data.get("strengths_identified", []),
                areas_for_focus=data.get("areas_for_focus", []),
                recommended_next_topics=data.get("recommended_next_topics", []),
                engagement_level=data.get("engagement_level", "medium"),
                suggested_modifications=data.get("suggested_modifications", []),
                celebration_message=data.get("celebration_message", f"Amazing effort today, {profile.name}! 🌟"),
                parent_notes=data.get("parent_notes", "Great session! Keep celebrating their effort."),
            )
        except Exception as exc:
            logger.error("analyze_progress failed: %s", exc)
            return ProgressInsight(
                overall_progress="growing",
                strengths_identified=["Showed up and tried their best", "Asked great questions"],
                areas_for_focus=["Continue building confidence with current topics"],
                recommended_next_topics=["Next step in current subject"],
                engagement_level="medium",
                suggested_modifications=["Shorter sessions may improve focus", "Add more visual supports"],
                celebration_message=f"You are doing incredible things, {profile.name}! Every lesson makes you stronger! 🌟🎉",
                parent_notes="Your child worked hard today. Celebrate their effort, not just the results!",
            )


education_service = EducationService()
