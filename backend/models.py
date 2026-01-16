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

# New Models for Enhanced Features

class Appointment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    counselor_name: Optional[str] = None
    appointment_date: datetime
    appointment_type: str  # 'campus', 'external', 'online'
    status: str = "scheduled"  # scheduled, completed, cancelled, rescheduled
    notes: Optional[str] = None
    reminder_sent: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JournalEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: Optional[str] = None
    content: str
    prompt_type: Optional[str] = None  # guided, free, reflection
    sentiment: Optional[str] = None  # positive, neutral, negative
    tags: List[str] = []
    is_private: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityPost(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    username_display: str  # Anonymous username
    category: str  # stress, anxiety, depression, success, support
    title: str
    content: str
    is_anonymous: bool = True
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CommunityComment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    post_id: str
    user_id: str
    username_display: str
    content: str
    likes_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WeeklyInsight(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    week_start: datetime
    week_end: datetime
    average_mood: float
    mood_trend: str  # improving, stable, declining
    assessment_summary: dict
    triggers_identified: List[str] = []
    recommendations: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserGoal(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    goal_type: str  # mood_improvement, assessment_reduction, consistency
    target_value: int
    current_value: int
    deadline: Optional[datetime] = None
    status: str = "active"  # active, completed, abandoned
    created_at: datetime = Field(default_factory=datetime.utcnow)