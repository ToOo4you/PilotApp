"""
AI Chatbot Service
Natural language interface for dispatch operations and logistics management
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from backend.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class ChatContext(Enum):
    """Chat context/domain"""
    DISPATCH = "dispatch"
    DRIVER_MANAGEMENT = "driver_management"
    ROUTE_PLANNING = "route_planning"
    VEHICLE_MANAGEMENT = "vehicle_management"
    ANALYTICS = "analytics"
    GENERAL = "general"


@dataclass
class ChatMessage:
    """Chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str = None


@dataclass
class ChatResponse:
    """Chatbot response"""
    message: str
    action_type: Optional[str]  # e.g., "dispatch_job", "optimize_route"
    action_data: Optional[Dict[str, Any]]
    context: ChatContext
    confidence_score: float
    followup_questions: List[str]


class AIDispatchChatbot:
    """AI chatbot for dispatch and logistics operations"""
    
    def __init__(self):
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
        self.system_prompt = """
You are Highway Pilot, an AI assistant for autonomous logistics dispatch and vehicle management.
You help dispatchers, drivers, and managers with:
- Job assignments and routing
- Driver and vehicle management
- Route optimization
- Maintenance scheduling
- Performance analytics
- Demand forecasting
- Real-time operational guidance

Be concise, professional, and action-oriented. Always clarify ambiguous requests and confirm before taking actions.
Provide data-driven recommendations and explain your reasoning.
        """
    
    async def chat(
        self,
        user_message: str,
        session_id: str,
        context_data: Dict[str, Any] = None
    ) -> ChatResponse:
        """
        Process user message and generate response
        
        Args:
            user_message: User's message
            session_id: Chat session ID
            context_data: Contextual data (current shipments, drivers, etc.)
        
        Returns:
            ChatResponse with message and suggested actions
        """
        
        # Initialize conversation history for session
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Add user message to history
        self.conversation_history[session_id].append(
            ChatMessage(role="user", content=user_message, timestamp=datetime.now().isoformat())
        )
        
        # Build conversation context
        history_text = "\n".join([
            f"{msg.role.upper()}: {msg.content}"
            for msg in self.conversation_history[session_id][-10:]  # Last 10 messages
        ])
        
        context_text = ""
        if context_data:
            context_text = f"""
Current system state:
- Active drivers: {context_data.get('active_drivers', 0)}
- Pending jobs: {context_data.get('pending_jobs', 0)}
- Vehicles in use: {context_data.get('vehicles_in_use', 0)}
- Active routes: {context_data.get('active_routes', 0)}
            """
        
        prompt = f"""
{self.system_prompt}

{context_text}

Conversation history:
{history_text}

Current request: {user_message}

Respond with JSON containing:
- message: Your response to the user
- action_type: What action to take (or null if none)
- action_data: Data for the action (or null)
- context: The domain/context (dispatch, driver_management, etc.)
- confidence_score: Your confidence 0-100
- followup_questions: Suggested follow-up questions for the user

If the user is asking for an action (e.g., "Assign job X to driver Y"), include action_data.
        """
        
        try:
            response_text = await ai_service.call_ai(
                prompt,
                provider="openai",
                model="gpt-4",
                temperature=0.5
            )
            
            import json
            result = json.loads(response_text)
            
            # Add assistant message to history
            self.conversation_history[session_id].append(
                ChatMessage(role="assistant", content=result['message'], timestamp=datetime.now().isoformat())
            )
            
            return ChatResponse(
                message=result['message'],
                action_type=result.get('action_type'),
                action_data=result.get('action_data'),
                context=ChatContext[result.get('context', 'GENERAL').upper()],
                confidence_score=float(result.get('confidence_score', 0)) / 100,
                followup_questions=result.get('followup_questions', [])
            )
            
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            raise
    
    async def get_suggestions(
        self,
        session_id: str,
        context_type: ChatContext = ChatContext.GENERAL
    ) -> List[str]:
        """Get AI-powered suggestions for the user"""
        
        history_text = ""
        if session_id in self.conversation_history:
            history_text = "\n".join([
                msg.content for msg in self.conversation_history[session_id][-5:]
            ])
        
        prompt = f"""
Based on the recent conversation in {context_type.value}, suggest 3-5 helpful next actions or questions.
        
Recent conversation:
{history_text}

Provide as JSON array of strings (action suggestions).
        """
        
        try:
            response = await ai_service.call_ai(prompt, model="gpt-3.5-turbo")
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []
    
    async def resolve_ambiguity(
        self,
        user_message: str,
        possible_interpretations: List[str]
    ) -> Tuple[int, str]:
        """
        Help resolve ambiguous user requests
        
        Args:
            user_message: The ambiguous message
            possible_interpretations: List of possible interpretations
        
        Returns:
            Tuple of (best_interpretation_index, explanation)
        """
        
        interpretations_text = "\n".join([
            f"{i+1}. {interp}" for i, interp in enumerate(possible_interpretations)
        ])
        
        prompt = f"""
Help resolve this ambiguous user request:

User said: "{user_message}"

Possible interpretations:
{interpretations_text}

Which interpretation is most likely? Respond with JSON:
- interpretation_index: 1-based index of most likely interpretation
- explanation: Why you think this is the intended meaning
        """
        
        try:
            response = await ai_service.call_ai(prompt, model="gpt-3.5-turbo")
            import json
            result = json.loads(response)
            return (result['interpretation_index'] - 1, result['explanation'])
        except Exception as e:
            logger.error(f"Ambiguity resolution failed: {e}")
            return (0, "Unable to resolve")
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a session"""
        if session_id not in self.conversation_history:
            return []
        
        return [
            {"role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
            for msg in self.conversation_history[session_id]
        ]


chatbot = AIDispatchChatbot()
