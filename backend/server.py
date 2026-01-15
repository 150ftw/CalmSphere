from fastapi import FastAPI, APIRouter, HTTPException, Depends
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone

from models import (
    UserCreate, User, Token, UserProfile, ChatMessage, ChatSession,
    AssessmentResult, MoodEntry, SelfHelpModule, ConfigSettings,
    SendMessageRequest, StartAssessmentRequest, SubmitAssessmentRequest,
    MoodEntryRequest
)
from auth import hash_password, verify_password, create_access_token, verify_token
from risk_engine import detect_risk_level, get_crisis_response, get_high_risk_response
from content_selector import (
    get_assessment_questions, calculate_assessment_score,
    get_self_help_modules, select_modules_for_user
)

from emergentintegrations.llm.chat import LlmChat, UserMessage as LlmUserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# LLM System message
SYSTEM_MESSAGE = """You are CalmSphere AI, a supportive mental health companion for college students. Your role is to:

1. Listen empathetically and without judgment
2. Validate feelings and experiences
3. Ask clarifying questions to understand their situation better
4. Provide supportive, evidence-based coping strategies when appropriate
5. Be warm, genuine, and human in your responses
6. Keep responses concise (2-4 sentences usually)
7. NEVER diagnose mental health conditions
8. NEVER recommend medications
9. NEVER claim to be a therapist or doctor
10. Encourage professional help when appropriate
11. Focus on self-help, psycho-education, and healthy coping strategies

Remember: You are a supportive tool, not a replacement for professional mental health care. Be caring, but maintain appropriate boundaries."""

# Helper functions
async def get_config() -> dict:
    config = await db.config_settings.find_one({}, {"_id": 0})
    if not config:
        config = {
            "crisis_hotline": "988",
            "campus_counselor_phone": "Contact your campus health center",
            "campus_counselor_email": "Available through campus resources",
            "risk_threshold_high": 15,
            "risk_threshold_medium": 10
        }
    return config

async def get_latest_scores(user_id: str) -> dict:
    scores = {}
    for assessment_type in ['phq9', 'gad7', 'stress']:
        result = await db.assessment_results.find_one(
            {"user_id": user_id, "assessment_type": assessment_type},
            {"_id": 0},
            sort=[("timestamp", -1)]
        )
        if result:
            scores[assessment_type] = result['total_score']
    return scores

# Auth Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        is_pseudonymous=user_data.is_pseudonymous,
        role=user_data.role
    )
    
    user_dict = user.model_dump()
    user_dict['password_hash'] = hash_password(user_data.password)
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    
    await db.users.insert_one(user_dict)
    
    # Create token
    token = create_access_token({"user_id": user.id, "email": user.email, "role": user.role})
    
    return Token(access_token=token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(email: str, password: str):
    user_dict = await db.users.find_one({"email": email}, {"_id": 0})
    if not user_dict:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(password, user_dict['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Convert to User model
    user_dict.pop('password_hash')
    if isinstance(user_dict['created_at'], str):
        user_dict['created_at'] = datetime.fromisoformat(user_dict['created_at'])
    user = User(**user_dict)
    
    token = create_access_token({"user_id": user.id, "email": user.email, "role": user.role})
    
    return Token(access_token=token, token_type="bearer", user=user)

# Profile Routes
@api_router.post("/profile/onboarding")
async def complete_onboarding(profile_data: dict, token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    
    profile = UserProfile(
        user_id=user_id,
        year=profile_data.get('year'),
        branch=profile_data.get('branch'),
        concerns=profile_data.get('concerns', []),
        consent_given=profile_data.get('consent_given', False),
        timezone=profile_data.get('timezone'),
        onboarding_completed=True
    )
    
    profile_dict = profile.model_dump()
    profile_dict['created_at'] = profile_dict['created_at'].isoformat()
    
    await db.user_profiles.insert_one(profile_dict)
    
    return {"message": "Onboarding completed", "profile": profile}

@api_router.get("/profile")
async def get_profile(token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    profile = await db.user_profiles.find_one({"user_id": user_id}, {"_id": 0})
    return profile

# Chat Routes
@api_router.post("/chat/session/create")
async def create_chat_session(token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    
    session = ChatSession(user_id=user_id)
    session_dict = session.model_dump()
    session_dict['created_at'] = session_dict['created_at'].isoformat()
    session_dict['updated_at'] = session_dict['updated_at'].isoformat()
    
    await db.chat_sessions.insert_one(session_dict)
    
    return session

@api_router.get("/chat/sessions")
async def get_chat_sessions(token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    sessions = await db.chat_sessions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("updated_at", -1).to_list(50)
    
    for session in sessions:
        if isinstance(session.get('created_at'), str):
            session['created_at'] = datetime.fromisoformat(session['created_at'])
        if isinstance(session.get('updated_at'), str):
            session['updated_at'] = datetime.fromisoformat(session['updated_at'])
    
    return sessions

@api_router.get("/chat/session/{session_id}/messages")
async def get_chat_messages(session_id: str, token_data: dict = Depends(verify_token)):
    messages = await db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    for msg in messages:
        if isinstance(msg.get('timestamp'), str):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
    
    return messages

@api_router.post("/chat/send")
async def send_message(request: SendMessageRequest, token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    
    # Detect risk
    risk_level, risk_score = detect_risk_level(request.message)
    
    # Save user message
    user_message = ChatMessage(
        session_id=request.session_id,
        user_id=user_id,
        role="user",
        content=request.message,
        risk_level=risk_level
    )
    
    user_msg_dict = user_message.model_dump()
    user_msg_dict['timestamp'] = user_msg_dict['timestamp'].isoformat()
    await db.chat_messages.insert_one(user_msg_dict)
    
    # Update session timestamp
    await db.chat_sessions.update_one(
        {"id": request.session_id},
        {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Handle crisis
    if risk_level == 'crisis':
        config = await get_config()
        crisis_msg = get_crisis_response(config)
        
        assistant_message = ChatMessage(
            session_id=request.session_id,
            user_id=user_id,
            role="assistant",
            content=crisis_msg,
            risk_level="crisis"
        )
        
        assist_msg_dict = assistant_message.model_dump()
        assist_msg_dict['timestamp'] = assist_msg_dict['timestamp'].isoformat()
        await db.chat_messages.insert_one(assist_msg_dict)
        
        return {
            "message": assistant_message,
            "risk_level": "crisis",
            "show_crisis_resources": True
        }
    
    # Get conversation history
    history = await db.chat_messages.find(
        {"session_id": request.session_id},
        {"_id": 0}
    ).sort("timestamp", 1).limit(20).to_list(20)
    
    # Call LLM
    try:
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        chat = LlmChat(
            api_key=api_key,
            session_id=request.session_id,
            system_message=SYSTEM_MESSAGE
        ).with_model("openai", "gpt-5.2")
        
        llm_message = LlmUserMessage(text=request.message)
        response = await chat.send_message(llm_message)
        
        # Add high risk note if needed
        if risk_level == 'high':
            response += "\n\n" + get_high_risk_response()
        
    except Exception as e:
        logging.error(f"LLM error: {e}")
        response = "I'm having trouble connecting right now. Please try again in a moment. If you're in crisis, please reach out to a crisis hotline or emergency services immediately."
    
    # Save assistant response
    assistant_message = ChatMessage(
        session_id=request.session_id,
        user_id=user_id,
        role="assistant",
        content=response,
        risk_level=risk_level
    )
    
    assist_msg_dict = assistant_message.model_dump()
    assist_msg_dict['timestamp'] = assist_msg_dict['timestamp'].isoformat()
    await db.chat_messages.insert_one(assist_msg_dict)
    
    # Get recommended modules
    latest_scores = await get_latest_scores(user_id)
    modules = select_modules_for_user(latest_scores, "stable", risk_level)
    
    return {
        "message": assistant_message,
        "risk_level": risk_level,
        "recommended_modules": modules[:2] if modules else [],
        "show_crisis_resources": risk_level in ['crisis', 'high']
    }

# Assessment Routes
@api_router.get("/assessment/questions/{assessment_type}")
async def get_questions(assessment_type: str, token_data: dict = Depends(verify_token)):
    questions = get_assessment_questions(assessment_type)
    if not questions:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return {"assessment_type": assessment_type, "questions": questions}

@api_router.post("/assessment/submit")
async def submit_assessment(request: SubmitAssessmentRequest, token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    
    total_score, severity = calculate_assessment_score(request.assessment_type, request.responses)
    
    result = AssessmentResult(
        user_id=user_id,
        assessment_type=request.assessment_type,
        responses=request.responses,
        total_score=total_score,
        severity=severity
    )
    
    result_dict = result.model_dump()
    result_dict['timestamp'] = result_dict['timestamp'].isoformat()
    await db.assessment_results.insert_one(result_dict)
    
    return result

@api_router.get("/assessment/history/{assessment_type}")
async def get_assessment_history(assessment_type: str, token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    
    results = await db.assessment_results.find(
        {"user_id": user_id, "assessment_type": assessment_type},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(50)
    
    for result in results:
        if isinstance(result.get('timestamp'), str):
            result['timestamp'] = datetime.fromisoformat(result['timestamp'])
    
    return results

# Mood Routes
@api_router.post("/mood/log")
async def log_mood(request: MoodEntryRequest, token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    
    entry = MoodEntry(
        user_id=user_id,
        mood_rating=request.mood_rating,
        tags=request.tags,
        note=request.note
    )
    
    entry_dict = entry.model_dump()
    entry_dict['timestamp'] = entry_dict['timestamp'].isoformat()
    await db.mood_entries.insert_one(entry_dict)
    
    return entry

@api_router.get("/mood/history")
async def get_mood_history(token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    
    entries = await db.mood_entries.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("timestamp", -1).to_list(100)
    
    for entry in entries:
        if isinstance(entry.get('timestamp'), str):
            entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
    
    return entries

# Self-help modules
@api_router.get("/modules")
async def get_modules(token_data: dict = Depends(verify_token)):
    return get_self_help_modules()

# Dashboard data
@api_router.get("/dashboard/student")
async def get_student_dashboard(token_data: dict = Depends(verify_token)):
    user_id = token_data['user_id']
    
    # Get latest mood
    latest_mood = await db.mood_entries.find_one(
        {"user_id": user_id},
        {"_id": 0},
        sort=[("timestamp", -1)]
    )
    
    # Get latest scores
    latest_scores = await get_latest_scores(user_id)
    
    # Get recent sessions
    recent_sessions = await db.chat_sessions.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("updated_at", -1).limit(5).to_list(5)
    
    return {
        "latest_mood": latest_mood,
        "latest_scores": latest_scores,
        "recent_sessions": recent_sessions
    }

# Admin Analytics Routes
@api_router.get("/admin/analytics")
async def get_analytics(token_data: dict = Depends(verify_token)):
    if token_data.get('role') != 'counselor':
        raise HTTPException(status_code=403, detail="Counselor access required")
    
    # Aggregate PHQ-9 scores
    phq9_pipeline = [
        {"$match": {"assessment_type": "phq9"}},
        {"$group": {
            "_id": "$severity",
            "count": {"$sum": 1}
        }}
    ]
    phq9_dist = await db.assessment_results.aggregate(phq9_pipeline).to_list(10)
    
    # Aggregate GAD-7 scores
    gad7_pipeline = [
        {"$match": {"assessment_type": "gad7"}},
        {"$group": {
            "_id": "$severity",
            "count": {"$sum": 1}
        }}
    ]
    gad7_dist = await db.assessment_results.aggregate(gad7_pipeline).to_list(10)
    
    # Count active users
    total_users = await db.users.count_documents({"role": "student"})
    total_sessions = await db.chat_sessions.count_documents({})
    total_assessments = await db.assessment_results.count_documents({})
    
    return {
        "phq9_distribution": phq9_dist,
        "gad7_distribution": gad7_dist,
        "total_users": total_users,
        "total_sessions": total_sessions,
        "total_assessments": total_assessments
    }

@api_router.get("/admin/config")
async def get_admin_config(token_data: dict = Depends(verify_token)):
    if token_data.get('role') != 'counselor':
        raise HTTPException(status_code=403, detail="Counselor access required")
    return await get_config()

@api_router.post("/admin/config")
async def update_config(config_data: dict, token_data: dict = Depends(verify_token)):
    if token_data.get('role') != 'counselor':
        raise HTTPException(status_code=403, detail="Counselor access required")
    
    config_data['updated_at'] = datetime.now(timezone.utc).isoformat()
    await db.config_settings.delete_many({})
    await db.config_settings.insert_one(config_data)
    
    return {"message": "Config updated"}

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()