from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
import uuid

class UserCreate(BaseModel):
    email: str
    password: str
    username: str
    is_pseudonymous: bool = False
    role: str = "student"

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    is_pseudonymous: bool
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    year: Optional[str] = None
    branch: Optional[str] = None
    concerns: List[str] = []
    consent_given: bool = False
    timezone: Optional[str] = None
    onboarding_completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    role: str  # 'user' or 'assistant'
    content: str
    risk_level: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: Optional[str] = "New Conversation"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AssessmentResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    assessment_type: str  # 'phq9', 'gad7', 'stress'
    responses: dict
    total_score: int
    severity: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MoodEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    mood_rating: int  # 1-10
    tags: List[str] = []
    note: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SelfHelpModule(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    module_type: str  # breathing, grounding, cbt, journaling, etc.
    description: str
    content: dict
    tags: List[str] = []
    difficulty: str = "beginner"

class ConfigSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    crisis_hotline: str = "1800-599-0019"  # KIRAN Mental Health Helpline
    campus_counselor_phone: Optional[str] = None
    campus_counselor_email: Optional[str] = None
    risk_threshold_high: int = 15
    risk_threshold_medium: int = 10
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SendMessageRequest(BaseModel):
    session_id: str
    message: str

class StartAssessmentRequest(BaseModel):
    assessment_type: str

class SubmitAssessmentRequest(BaseModel):
    assessment_type: str
    responses: dict

class MoodEntryRequest(BaseModel):
    mood_rating: int
    tags: List[str] = []
    note: Optional[str] = None