from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(str(ROOT_DIR / '.env'))
print("MONGO_URL:", os.getenv('MONGO_URL'))
print("DB_NAME:", os.getenv('DB_NAME'))
print("EMERGENT_LLM_KEY:", os.getenv('EMERGENT_LLM_KEY'))

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
# Use local MongoDB - no SSL configuration needed
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# LLM Integration setup
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    llm_key = os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-b68E9Cb0642462aB11')
except ImportError:
    print("Warning: emergentintegrations not installed. LLM features will be disabled.")
    LlmChat = None
    UserMessage = None
    llm_key = None

# Enums
class Subject(str, Enum):
    MATH = "math"
    SOCIAL_STUDIES = "social_studies"

class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Language(str, Enum):
    ENGLISH = "english"
    ODIA = "odia"

# Models
class Student(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int
    grade: int  # 1 or 2
    avatar: str
    language: Language = Language.ENGLISH
    total_xp: int = 0
    level: int = 1
    current_streak: int = 0
    best_streak: int = 0
    badges: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Quest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    title_odia: str
    description: str
    description_odia: str
    subject: Subject
    grade: int
    difficulty: Difficulty
    xp_reward: int
    story_context: str
    story_context_odia: str
    questions: List[Dict[str, Any]]
    is_unlocked: bool = True
    order: int = 0

class Progress(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    quest_id: str
    completed: bool = False
    score: int = 0
    attempts: int = 0
    last_attempt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    xp_earned: int = 0

class StudentCreate(BaseModel):
    name: str
    age: int
    grade: int
    avatar: str
    language: Language = Language.ENGLISH

class QuestionAnswer(BaseModel):
    question_id: str
    answer: str

class QuestSubmission(BaseModel):
    quest_id: str
    answers: List[QuestionAnswer]

# Helper functions
def prepare_for_mongo(data):
    """Convert datetime objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
            elif isinstance(value, dict):
                data[key] = prepare_for_mongo(value)
            elif isinstance(value, list):
                data[key] = [prepare_for_mongo(item) if isinstance(item, dict) else item for item in value]
    return data

def parse_from_mongo(data):
    """Parse datetime strings back from MongoDB"""
    if isinstance(data, dict):
        for key, value in data.items():
            if key in ['created_at', 'last_activity', 'last_attempt'] and isinstance(value, str):
                try:
                    data[key] = datetime.fromisoformat(value)
                except:
                    data[key] = datetime.now(timezone.utc)
    return data

async def get_llm_chat(provider: str, model: str, system_message: str, session_id: str):
    """Initialize LLM chat with specified provider and model"""
    if not LlmChat or not llm_key:
        return None
    
    chat = LlmChat(
        api_key=llm_key,
        session_id=session_id,
        system_message=system_message
    )
    
    if provider == "openai":
        chat.with_model("openai", model)
    elif provider == "anthropic":
        chat.with_model("anthropic", model)
    elif provider == "gemini":
        chat.with_model("gemini", model)
    
    return chat

# Predefined bilingual content - Expanded Curriculum
PREDEFINED_QUESTS = [
    # MATH - GRADE 1
    {
        "title": "Help the Farmer Count Mangoes",
        "title_odia": "କୃଷକଙ୍କୁ ଆମ୍ବ ଗଣିବାରେ ସାହାଯ୍ୟ କରନ୍ତୁ",
        "description": "Learn counting 1-50 by helping farmer Raju count mangoes",
        "description_odia": "କୃଷକ ରାଜୁଙ୍କୁ ଆମ୍ବ ଗଣିବାରେ ସାହାଯ୍ୟ କରି ୧-୫୦ ଗଣନା ଶିଖନ୍ତୁ",
        "subject": Subject.MATH,
        "grade": 1,
        "difficulty": Difficulty.EASY,
        "xp_reward": 50,
        "story_context": "In Puri village, farmer Raju grows the sweetest mangoes in all of Odisha! Help him count his harvest.",
        "story_context_odia": "ପୁରୀ ଗାଁରେ, କୃଷକ ରାଜୁ ସମଗ୍ର ଓଡ଼ିଶାରେ ସବୁଠାରୁ ମିଠା ଆମ୍ବ ଚାଷ କରନ୍ତି! ତାଙ୍କର ଅମଳ ଗଣିବାରେ ସାହାଯ୍ୟ କରନ୍ତୁ।",
        "questions": [
            {
                "id": "q1",
                "question": "How many mangoes do you see on the tree?",
                "question_odia": "ଗଛରେ ତୁମେ କେତୋଟି ଆମ୍ବ ଦେଖୁଛ?",
                "type": "counting",
                "image_url": "https://images.unsplash.com/photo-1502086223501-7ea6ecd79368",
                "correct_answer": "15",
                "options": ["12", "15", "18", "20"]
            }
        ],
        "order": 1
    },
    {
        "title": "Shape Detective in Konark Temple",
        "title_odia": "କୋଣାର୍କ ମନ୍ଦିରରେ ଆକୃତି ଗୋଇଣ୍ଡା",
        "description": "Discover shapes and patterns in the famous Konark Sun Temple",
        "description_odia": "ପ୍ରସିଦ୍ଧ କୋଣାର୍କ ସୂର୍ଯ୍ୟ ମନ୍ଦିରରେ ଆକୃତି ଏବଂ ନମୁନା ଆବିଷ୍କାର କରନ୍ତୁ",
        "subject": Subject.MATH,
        "grade": 1,
        "difficulty": Difficulty.EASY,
        "xp_reward": 60,
        "story_context": "The ancient Konark Temple has beautiful patterns carved in stone. Let's explore geometric shapes!",
        "story_context_odia": "ପ୍ରାଚୀନ କୋଣାର୍କ ମନ୍ଦିରରେ ପଥରରେ ଖୋଦିତ ସୁନ୍ଦର ନମୁନା ଅଛି। ଚାଲ ଜ୍ୟାମିତିକ ଆକୃତି ଅନ୍ୱେଷଣ କରିବା!",
        "questions": [
            {
                "id": "q1",
                "question": "What shape is the wheel of Konark temple?",
                "question_odia": "କୋଣାର୍କ ମନ୍ଦିରର ଚକ କି ଆକୃତିର?",
                "type": "multiple_choice",
                "correct_answer": "Circle",
                "options": ["Square", "Triangle", "Circle", "Rectangle"]
            }
        ],
        "order": 2
    },
    # MATH - GRADE 2
    {
        "title": "Jagannath Temple Market Addition",
        "title_odia": "ଜଗନ୍ନାଥ ମନ୍ଦିର ବଜାର ଯୋଗ",
        "description": "Practice addition up to 100 while shopping in Puri market",
        "description_odia": "ପୁରୀ ବଜାରରେ କିଣାକାଟା କରିବା ସମୟରେ ୧୦୦ ପର୍ଯ୍ୟନ୍ତ ଯୋଗ ଅଭ୍ୟାସ କରନ୍ତୁ",
        "subject": Subject.MATH,
        "grade": 2,
        "difficulty": Difficulty.MEDIUM,
        "xp_reward": 70,
        "story_context": "Visit the bustling Puri market near Jagannath Temple and help the shopkeeper calculate prices!",
        "story_context_odia": "ଜଗନ୍ନାଥ ମନ୍ଦିର ନିକଟସ୍ଥ ବ୍ୟସ୍ତବହୁଳ ପୁରୀ ବଜାର ପରିଦର୍ଶନ କରନ୍ତୁ ଏବଂ ଦୋକାନୀଙ୍କୁ ଦାମ ଗଣନା କରିବାରେ ସାହାଯ୍ୟ କରନ୍ତୁ!",
        "questions": [
            {
                "id": "q1",
                "question": "If prasad costs 45 rupees and flowers cost 35 rupees, what's the total?",
                "question_odia": "ଯଦି ପ୍ରସାଦ ୪୫ ଟଙ୍କା ଏବଂ ଫୁଲ ୩୫ ଟଙ୍କା, ମୋଟ କେତେ?",
                "type": "word_problem",
                "correct_answer": "80",
                "options": ["75", "80", "85", "90"]
            }
        ],
        "order": 3
    },
    {
        "title": "Time for Odissi Dance Class",
        "title_odia": "ଓଡ଼ିଶୀ ନୃତ୍ୟ କ୍ଲାସ ପାଇଁ ସମୟ",
        "description": "Learn to tell time with hours and half-hours during dance practice",
        "description_odia": "ନୃତ୍ୟ ଅଭ୍ୟାସ ସମୟରେ ଘଣ୍ଟା ଏବଂ ଅଧା ଘଣ୍ଟା ସହିତ ସମୟ କହିବା ଶିଖନ୍ତୁ",
        "subject": Subject.MATH,
        "grade": 2,
        "difficulty": Difficulty.MEDIUM,
        "xp_reward": 75,
        "story_context": "Maya learns classical Odissi dance. Help her understand when her classes start!",
        "story_context_odia": "ମାୟାକ୍ଳାସିକ୍ ଓଡ଼ିଶୀ ନୃତ୍ୟ ଶିଖୁଛି। ତାର କ୍ଲାସ କେବେ ଆରମ୍ଭ ହୁଏ ବୁଝିବାରେ ସାହାଯ୍ୟ କରନ୍ତୁ!",
        "questions": [
            {
                "id": "q1",
                "question": "What time does the clock show?",
                "question_odia": "ଘଣ୍ଟା କେତେ ସମୟ ଦେଖାଉଛି?",
                "type": "time_reading",
                "image_url": "https://images.unsplash.com/photo-1586737640555-2b60ee02b869",
                "correct_answer": "3:30",
                "options": ["3:00", "3:30", "4:00", "4:30"]
            }
        ],
        "order": 4
    },
    # SOCIAL STUDIES - GRADE 1
    {
        "title": "My Odisha Family Tree",
        "title_odia": "ମୋର ଓଡ଼ିଶା ପରିବାର ବୃକ୍ଷ",
        "description": "Learn about family relationships and Odia traditions",
        "description_odia": "ପାରିବାରିକ ସମ୍ପର୍କ ଏବଂ ଓଡ଼ିଆ ପରମ୍ପରା ବିଷୟରେ ଜାଣନ୍ତୁ",
        "subject": Subject.SOCIAL_STUDIES,
        "grade": 1,
        "difficulty": Difficulty.EASY,
        "xp_reward": 55,
        "story_context": "Meet little Arjun's family from Bhubaneswar. Learn about different family members and their roles!",
        "story_context_odia": "ଭୁବନେଶ୍ୱରର ଛୋଟ ଅର୍ଜୁନଙ୍କ ପରିବାରକୁ ଭେଟନ୍ତୁ। ବିଭିନ୍ନ ପରିବାର ସଦସ୍ୟ ଏବଂ ସେମାନଙ୍କର ଭୂମିକା ବିଷୟରେ ଜାଣନ୍ତୁ!",
        "questions": [
            {
                "id": "q1",
                "question": "Who takes care of children when parents are working?",
                "question_odia": "ବାବା ମା କାମରେ ଥିବା ସମୟରେ ପିଲାମାନଙ୍କର ଯତ୍ନ କିଏ ନିଅନ୍ତି?",
                "type": "multiple_choice",
                "correct_answer": "Grandparents",
                "options": ["Grandparents", "Neighbors", "Teachers", "Friends"]
            }
        ],
        "order": 5
    },
    {
        "title": "Community Helpers in Our Village",
        "title_odia": "ଆମ ଗାଁର ସମୁଦାୟ ସାହାଯ୍ୟକାରୀ",
        "description": "Meet the helpful people who make our community strong",
        "description_odia": "ଆମ ସମୁଦାୟକୁ ଶକ୍ତିଶାଳୀ କରୁଥିବା ସାହାଯ୍ୟକାରୀ ଲୋକଙ୍କୁ ଭେଟନ୍ତୁ",
        "subject": Subject.SOCIAL_STUDIES,
        "grade": 1,
        "difficulty": Difficulty.EASY,
        "xp_reward": 50,
        "story_context": "In every Odisha village, special people help everyone. Let's learn about community helpers!",
        "story_context_odia": "ପ୍ରତ୍ୟେକ ଓଡ଼ିଶା ଗାଁରେ, ବିଶେଷ ଲୋକମାନେ ସମସ୍ତଙ୍କୁ ସାହାଯ୍ୟ କରନ୍ତି। ଚାଲ ସମୁଦାୟ ସାହାଯ୍ୟକାରୀଙ୍କ ବିଷୟରେ ଜାଣିବା!",
        "questions": [
            {
                "id": "q1",
                "question": "Who helps when someone is sick?",
                "question_odia": "କେହି ଅସୁସ୍ଥ ହେଲେ କିଏ ସାହାଯ୍ୟ କରେ?",
                "type": "multiple_choice",
                "correct_answer": "Doctor",
                "options": ["Teacher", "Doctor", "Farmer", "Cook"]
            }
        ],
        "order": 6
    },
    # SOCIAL STUDIES - GRADE 2  
    {
        "title": "Protect the Village - Learn About Rivers",
        "title_odia": "ଗାଁକୁ ରକ୍ଷା କର - ନଦୀ ବିଷୟରେ ଜାଣ",
        "description": "Discover Odisha's sacred rivers and their importance",
        "description_odia": "ଓଡ଼ିଶାର ପବିତ୍ର ନଦୀ ଏବଂ ସେମାନଙ୍କର ଗୁରୁତ୍ୱ ଆବିଷ୍କାର କରନ୍ତୁ",
        "subject": Subject.SOCIAL_STUDIES,
        "grade": 2,
        "difficulty": Difficulty.MEDIUM,
        "xp_reward": 80,
        "story_context": "Learn about Odisha's mighty rivers - Mahanadi, Brahmani, and Baitarani - and how they help our state!",
        "story_context_odia": "ଓଡ଼ିଶାର ଶକ୍ତିଶାଳୀ ନଦୀ - ମହାନଦୀ, ବ୍ରାହ୍ମଣୀ, ଏବଂ ବୈତରଣୀ - ଏବଂ ସେମାନେ କିପରି ଆମ ରାଜ୍ୟକୁ ସାହାଯ୍ୟ କରନ୍ତି!",
        "questions": [
            {
                "id": "q1",
                "question": "Which is the longest river in Odisha?",
                "question_odia": "ଓଡ଼ିଶାର ସବୁଠାରୁ ଲମ୍ବା ନଦୀ କେଉଁଟି?",
                "type": "multiple_choice",
                "correct_answer": "Mahanadi",
                "options": ["Brahmani", "Mahanadi", "Baitarani", "Subarnarekha"]
            }
        ],
        "order": 7
    },
    {
        "title": "Famous People of Odisha",
        "title_odia": "ଓଡ଼ିଶାର ପ୍ରସିଦ୍ଧ ବ୍ୟକ୍ତିତ୍ୱ",
        "description": "Learn about heroes and great people from our state",
        "description_odia": "ଆମ ରାଜ୍ୟର ବୀର ଏବଂ ମହାନ ବ୍ୟକ୍ତିଙ୍କ ବିଷୟରେ ଜାଣନ୍ତୁ",
        "subject": Subject.SOCIAL_STUDIES,
        "grade": 2,
        "difficulty": Difficulty.MEDIUM,
        "xp_reward": 85,
        "story_context": "Meet the inspiring people who made Odisha proud - from ancient kings to modern heroes!",
        "story_context_odia": "ପ୍ରେରଣାଦାୟକ ବ୍ୟକ୍ତିମାନଙ୍କୁ ଭେଟନ୍ତୁ ଯେଉଁମାନେ ଓଡ଼ିଶାକୁ ଗର୍ବିତ କରିଛନ୍ତି - ପ୍ରାଚୀନ ରାଜାଙ୍କଠାରୁ ଆଧୁନିକ ବୀର ପର୍ଯ୍ୟନ୍ତ!",
        "questions": [
            {
                "id": "q1",
                "question": "Who was the great king that built the Jagannath Temple?",
                "question_odia": "ଜଗନ୍ନାଥ ମନ୍ଦିର ନିର୍ମାଣ କରୁଥିବା ମହାନ ରାଜା କିଏ ଥିଲେ?",
                "type": "multiple_choice",
                "correct_answer": "King Anantavarman",
                "options": ["King Anantavarman", "King Narasimhadeva", "King Kapilendradeva", "King Purusottamdeva"]
            }
        ],
        "order": 8
    }
]

BADGES = {
    "first_quest": {"name": "First Steps", "name_odia": "ପ୍ରଥମ ପଦକ୍ଷେପ", "icon": "🌟"},
    "math_wizard": {"name": "Math Wizard", "name_odia": "ଗଣିତ ଯାଦୁଗର", "icon": "🧙‍♂️"},
    "village_protector": {"name": "Village Protector", "name_odia": "ଗାଁର ରକ୍ଷକ", "icon": "🛡️"},
    "streak_master": {"name": "7-Day Streak Master", "name_odia": "୭ ଦିନର ଧାରା ଗୁରୁ", "icon": "🔥"},
    "knowledge_seeker": {"name": "Knowledge Seeker", "name_odia": "ଜ୍ଞାନ ଅନ୍ୱେଷୀ", "icon": "📚"}
}

# Routes
@api_router.get("/")
async def root():
    return {"message": "Welcome to EduQuest Odisha!", "message_odia": "ଏଡୁକ୍ୱେଷ୍ଟ ଓଡ଼ିଶାରେ ସ୍ୱାଗତ!"}

@api_router.post("/students", response_model=Student)
async def create_student(student_data: StudentCreate):
    student = Student(**student_data.dict())
    student_dict = prepare_for_mongo(student.dict())
    await db.students.insert_one(student_dict)
    return student

@api_router.get("/students/{student_id}", response_model=Student)
async def get_student(student_id: str):
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return Student(**parse_from_mongo(student))

@api_router.get("/quests", response_model=List[Quest])
async def get_quests(grade: Optional[int] = None, subject: Optional[Subject] = None):
    # Initialize predefined quests if not in database
    existing_count = await db.quests.count_documents({})
    if existing_count == 0:
        for quest_data in PREDEFINED_QUESTS:
            quest = Quest(**quest_data)
            quest_dict = prepare_for_mongo(quest.dict())
            await db.quests.insert_one(quest_dict)
    
    # Build query
    query = {}
    if grade:
        query["grade"] = grade
    if subject:
        query["subject"] = subject
    
    quests = await db.quests.find(query).sort("order", 1).to_list(length=None)
    return [Quest(**parse_from_mongo(quest)) for quest in quests]

@api_router.get("/students/{student_id}/progress")
async def get_student_progress(student_id: str):
    progress_records = await db.progress.find({"student_id": student_id}).to_list(length=None)
    return [Progress(**parse_from_mongo(record)) for record in progress_records]

@api_router.post("/students/{student_id}/submit_quest")
async def submit_quest(student_id: str, submission: QuestSubmission):
    # Get student and quest
    student = await db.students.find_one({"id": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    quest = await db.quests.find_one({"id": submission.quest_id})
    if not quest:
        raise HTTPException(status_code=404, detail="Quest not found")
    
    # Calculate score
    correct_answers = 0
    total_questions = len(quest["questions"])
    
    for answer in submission.answers:
        question = next((q for q in quest["questions"] if q["id"] == answer.question_id), None)
        if question and question["correct_answer"].lower() == answer.answer.lower():
            correct_answers += 1
    
    score = int((correct_answers / total_questions) * 100)
    xp_earned = quest["xp_reward"] if score >= 70 else int(quest["xp_reward"] * 0.5)
    
    # Update or create progress
    existing_progress = await db.progress.find_one({
        "student_id": student_id,
        "quest_id": submission.quest_id
    })
    
    if existing_progress:
        # Update existing progress
        await db.progress.update_one(
            {"id": existing_progress["id"]},
            {
                "$set": {
                    "score": max(existing_progress.get("score", 0), score),
                    "completed": score >= 70,
                    "last_attempt": datetime.now(timezone.utc).isoformat(),
                    "xp_earned": max(existing_progress.get("xp_earned", 0), xp_earned)
                },
                "$inc": {"attempts": 1}
            }
        )
    else:
        # Create new progress
        progress = Progress(
            student_id=student_id,
            quest_id=submission.quest_id,
            completed=score >= 70,
            score=score,
            attempts=1,
            xp_earned=xp_earned
        )
        progress_dict = prepare_for_mongo(progress.dict())
        await db.progress.insert_one(progress_dict)
    
    # Update student stats
    new_badges = []
    update_fields = {
        "total_xp": student["total_xp"] + xp_earned,
        "level": (student["total_xp"] + xp_earned) // 100 + 1,
        "last_activity": datetime.now(timezone.utc).isoformat()
    }
    
    # Check for new badges
    if score >= 70 and "first_quest" not in student["badges"]:
        new_badges.append("first_quest")
    
    if quest["subject"] == "math" and score >= 90 and "math_wizard" not in student["badges"]:
        new_badges.append("math_wizard")
    
    if quest["subject"] == "social_studies" and score >= 90 and "village_protector" not in student["badges"]:
        new_badges.append("village_protector")
    
    if new_badges:
        update_fields["badges"] = student["badges"] + new_badges
    
    await db.students.update_one({"id": student_id}, {"$set": update_fields})
    
    return {
        "score": score,
        "xp_earned": xp_earned,
        "completed": score >= 70,
        "new_badges": new_badges,
        "correct_answers": correct_answers,
        "total_questions": total_questions
    }

@api_router.post("/students/{student_id}/generate_hint")
async def generate_hint(student_id: str, quest_id: str, question_id: str):
    """Generate personalized hint using GPT-4o for storytelling"""
    if not LlmChat:
        return {"hint": "Try counting carefully!", "hint_odia": "ଯତ୍ନ ସହିତ ଗଣନା କରିବାକୁ ଚେଷ୍ଟା କର!"}
    
    try:
        quest = await db.quests.find_one({"id": quest_id})
        if not quest:
            raise HTTPException(status_code=404, detail="Quest not found")
        
        question = next((q for q in quest["questions"] if q["id"] == question_id), None)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Use GPT-4o for creative, story-based hints
        system_message = f"""You are a helpful tutor for young students (age 6-8) in rural Odisha. 
        Create encouraging, story-based hints that relate to the quest context: {quest['story_context']}
        Keep hints simple, fun, and culturally relevant to Odisha village life.
        Always provide both English and Odia versions."""
        
        chat = await get_llm_chat("openai", "gpt-4o", system_message, f"hint_{student_id}")
        
        prompt = f"""Question: {question['question']}
        Context: {quest['story_context']}
        
        Give a gentle, encouraging hint without revealing the answer. Make it story-based and fun!
        
        Format your response as:
        English: [hint in English]
        Odia: [hint in Odia]"""
        
        message = UserMessage(text=prompt)
        response = await chat.send_message(message)
        
        # Parse response
        lines = response.strip().split('\n')
        hint_en = "Try counting step by step!"
        hint_od = "ଧାପେ ଧାପେ ଗଣନା କରିବାକୁ ଚେଷ୍ଟା କର!"
        
        for line in lines:
            if line.startswith("English:"):
                hint_en = line.replace("English:", "").strip()
            elif line.startswith("Odia:"):
                hint_od = line.replace("Odia:", "").strip()
        
        return {"hint": hint_en, "hint_odia": hint_od}
        
    except Exception as e:
        return {"hint": "You can do this! Take your time and think step by step.", 
                "hint_odia": "ତୁମେ ଏହା କରିପାର! ସମୟ ନିଅ ଏବଂ ଧାପେ ଧାପେ ଚିନ୍ତା କର।"}

@api_router.get("/leaderboard")
async def get_leaderboard(grade: Optional[int] = None, limit: int = 10):
    """Get student leaderboard"""
    query = {}
    if grade:
        query["grade"] = grade
    
    students = await db.students.find(query).sort("total_xp", -1).limit(limit).to_list(length=None)
    
    leaderboard = []
    for i, student in enumerate(students):
        leaderboard.append({
            "rank": i + 1,
            "name": student["name"],
            "total_xp": student["total_xp"],
            "level": student["level"],
            "avatar": student["avatar"],
            "badges_count": len(student.get("badges", []))
        })
    
    return leaderboard

@api_router.get("/badges")
async def get_badges():
    """Get all available badges"""
    return BADGES

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()