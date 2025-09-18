#!/usr/bin/env python3
"""
EduQuest Odisha Backend API Testing Suite
Tests all backend functionality including multi-LLM integration, student management,
gamification, quest system, and progress tracking.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

# Backend URL from frontend/.env
BACKEND_URL = "https://eduquest-village.preview.emergentagent.com/api"

class EduQuestTester:
    def __init__(self):
        self.session = None
        self.test_student_id = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"    Details: {details}")
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {details}")
    
    async def test_root_endpoint(self):
        """Test the root API endpoint"""
        try:
            async with self.session.get(f"{BACKEND_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "message_odia" in data:
                        self.log_test("Root Endpoint", True, "Bilingual welcome message received")
                        return True
                    else:
                        self.log_test("Root Endpoint", False, "Missing bilingual messages")
                        return False
                else:
                    self.log_test("Root Endpoint", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Exception: {str(e)}")
            return False
    
    async def test_student_registration(self):
        """Test student registration with realistic Odisha student data"""
        student_data = {
            "name": "Ananya Patel",
            "age": 7,
            "grade": 1,
            "avatar": "girl",
            "language": "english"
        }
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/students",
                json=student_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if all(key in data for key in ["id", "name", "age", "grade", "avatar", "total_xp", "level"]):
                        self.test_student_id = data["id"]
                        self.log_test("Student Registration", True, f"Student created with ID: {self.test_student_id}")
                        return True
                    else:
                        self.log_test("Student Registration", False, "Missing required fields in response")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Student Registration", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Student Registration", False, f"Exception: {str(e)}")
            return False
    
    async def test_student_profile_retrieval(self):
        """Test retrieving student profile"""
        if not self.test_student_id:
            self.log_test("Student Profile Retrieval", False, "No test student ID available")
            return False
        
        try:
            async with self.session.get(f"{BACKEND_URL}/students/{self.test_student_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data["name"] == "Ananya Patel" and data["grade"] == 1:
                        self.log_test("Student Profile Retrieval", True, "Profile data matches registration")
                        return True
                    else:
                        self.log_test("Student Profile Retrieval", False, "Profile data mismatch")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Student Profile Retrieval", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Student Profile Retrieval", False, f"Exception: {str(e)}")
            return False
    
    async def test_expanded_curriculum_quests(self):
        """Test the expanded curriculum with 8 new quests covering diverse subjects"""
        try:
            # Test all quests - should have 8 quests total
            async with self.session.get(f"{BACKEND_URL}/quests") as response:
                if response.status == 200:
                    quests = await response.json()
                    if len(quests) != 8:
                        self.log_test("Expanded Curriculum - Quest Count", False, f"Expected 8 quests, got {len(quests)}")
                        return False
                    
                    # Verify quest subjects and grades distribution
                    math_quests = [q for q in quests if q["subject"] == "math"]
                    social_quests = [q for q in quests if q["subject"] == "social_studies"]
                    grade1_quests = [q for q in quests if q["grade"] == 1]
                    grade2_quests = [q for q in quests if q["grade"] == 2]
                    
                    if len(math_quests) != 4 or len(social_quests) != 4:
                        self.log_test("Expanded Curriculum - Subject Distribution", False, 
                                    f"Expected 4 Math + 4 Social Studies, got {len(math_quests)} Math + {len(social_quests)} Social")
                        return False
                    
                    if len(grade1_quests) != 4 or len(grade2_quests) != 4:
                        self.log_test("Expanded Curriculum - Grade Distribution", False,
                                    f"Expected 4 Grade 1 + 4 Grade 2, got {len(grade1_quests)} Grade 1 + {len(grade2_quests)} Grade 2")
                        return False
                    
                    # Verify specific quest topics as mentioned in review request
                    expected_topics = {
                        "math": ["counting", "shapes", "addition", "time"],
                        "social_studies": ["family", "community helpers", "rivers", "famous people"]
                    }
                    
                    # Check Math topics
                    math_titles = [q["title"].lower() for q in math_quests]
                    math_topics_found = []
                    if any("count" in title or "mango" in title for title in math_titles):
                        math_topics_found.append("counting")
                    if any("shape" in title or "konark" in title for title in math_titles):
                        math_topics_found.append("shapes")
                    if any("addition" in title or "market" in title for title in math_titles):
                        math_topics_found.append("addition")
                    if any("time" in title or "dance" in title for title in math_titles):
                        math_topics_found.append("time")
                    
                    # Check Social Studies topics
                    social_titles = [q["title"].lower() for q in social_quests]
                    social_topics_found = []
                    if any("family" in title for title in social_titles):
                        social_topics_found.append("family")
                    if any("community" in title or "helper" in title for title in social_titles):
                        social_topics_found.append("community helpers")
                    if any("river" in title for title in social_titles):
                        social_topics_found.append("rivers")
                    if any("famous" in title or "people" in title for title in social_titles):
                        social_topics_found.append("famous people")
                    
                    if len(math_topics_found) != 4:
                        self.log_test("Expanded Curriculum - Math Topics", False,
                                    f"Expected all 4 math topics (counting, shapes, addition, time), found: {math_topics_found}")
                        return False
                    
                    if len(social_topics_found) != 4:
                        self.log_test("Expanded Curriculum - Social Studies Topics", False,
                                    f"Expected all 4 social studies topics (family, community helpers, rivers, famous people), found: {social_topics_found}")
                        return False
                    
                    self.log_test("Expanded Curriculum - All 8 Quests", True, 
                                f"✅ All 8 quests loaded with correct subject/grade distribution and diverse topics")
                    
                else:
                    error_text = await response.text()
                    self.log_test("Expanded Curriculum - Quest Retrieval", False, f"HTTP {response.status}: {error_text}")
                    return False
            
            return True
                    
        except Exception as e:
            self.log_test("Expanded Curriculum", False, f"Exception: {str(e)}")
            return False

    async def test_bilingual_content_structure(self):
        """Test bilingual content (English/Odia) structure and quality"""
        try:
            async with self.session.get(f"{BACKEND_URL}/quests") as response:
                if response.status == 200:
                    quests = await response.json()
                    
                    for quest in quests:
                        # Check required bilingual fields
                        required_bilingual_fields = [
                            ("title", "title_odia"),
                            ("description", "description_odia"),
                            ("story_context", "story_context_odia")
                        ]
                        
                        for eng_field, odia_field in required_bilingual_fields:
                            if eng_field not in quest or odia_field not in quest:
                                self.log_test("Bilingual Content - Field Structure", False,
                                            f"Quest '{quest.get('title', 'Unknown')}' missing {eng_field} or {odia_field}")
                                return False
                            
                            if not quest[eng_field] or not quest[odia_field]:
                                self.log_test("Bilingual Content - Content Quality", False,
                                            f"Quest '{quest['title']}' has empty {eng_field} or {odia_field}")
                                return False
                        
                        # Check questions have bilingual content
                        for question in quest.get("questions", []):
                            if "question" not in question or "question_odia" not in question:
                                self.log_test("Bilingual Content - Question Structure", False,
                                            f"Question in quest '{quest['title']}' missing bilingual content")
                                return False
                            
                            if not question["question"] or not question["question_odia"]:
                                self.log_test("Bilingual Content - Question Quality", False,
                                            f"Question in quest '{quest['title']}' has empty bilingual content")
                                return False
                    
                    # Verify Odia content contains Odia script characters
                    sample_quest = quests[0]
                    odia_text = sample_quest["title_odia"]
                    
                    # Check for Odia Unicode characters (basic check)
                    has_odia_chars = any(ord(char) >= 0x0B00 and ord(char) <= 0x0B7F for char in odia_text)
                    
                    if has_odia_chars:
                        self.log_test("Bilingual Content - Odia Script", True,
                                    "✅ Odia content contains proper Odia script characters")
                    else:
                        self.log_test("Bilingual Content - Odia Script", False,
                                    "Odia content does not contain Odia script characters")
                        return False
                    
                    self.log_test("Bilingual Content Structure", True,
                                f"✅ All {len(quests)} quests have complete bilingual content structure")
                    return True
                    
                else:
                    error_text = await response.text()
                    self.log_test("Bilingual Content", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Bilingual Content", False, f"Exception: {str(e)}")
            return False

    async def test_quest_filtering_by_grade(self):
        """Test quest filtering by grade (Grade 1 vs Grade 2)"""
        try:
            # Test Grade 1 filtering
            async with self.session.get(f"{BACKEND_URL}/quests?grade=1") as response:
                if response.status == 200:
                    grade1_quests = await response.json()
                    if not all(q["grade"] == 1 for q in grade1_quests):
                        self.log_test("Quest Filtering - Grade 1", False, "Grade 1 filter returned non-Grade 1 quests")
                        return False
                    
                    if len(grade1_quests) != 4:
                        self.log_test("Quest Filtering - Grade 1 Count", False, f"Expected 4 Grade 1 quests, got {len(grade1_quests)}")
                        return False
                    
                    self.log_test("Quest Filtering - Grade 1", True, f"✅ Grade 1 filter working correctly ({len(grade1_quests)} quests)")
                else:
                    self.log_test("Quest Filtering - Grade 1", False, f"HTTP {response.status}")
                    return False
            
            # Test Grade 2 filtering
            async with self.session.get(f"{BACKEND_URL}/quests?grade=2") as response:
                if response.status == 200:
                    grade2_quests = await response.json()
                    if not all(q["grade"] == 2 for q in grade2_quests):
                        self.log_test("Quest Filtering - Grade 2", False, "Grade 2 filter returned non-Grade 2 quests")
                        return False
                    
                    if len(grade2_quests) != 4:
                        self.log_test("Quest Filtering - Grade 2 Count", False, f"Expected 4 Grade 2 quests, got {len(grade2_quests)}")
                        return False
                    
                    self.log_test("Quest Filtering - Grade 2", True, f"✅ Grade 2 filter working correctly ({len(grade2_quests)} quests)")
                else:
                    self.log_test("Quest Filtering - Grade 2", False, f"HTTP {response.status}")
                    return False
            
            # Test subject filtering
            async with self.session.get(f"{BACKEND_URL}/quests?subject=math") as response:
                if response.status == 200:
                    math_quests = await response.json()
                    if not all(q["subject"] == "math" for q in math_quests):
                        self.log_test("Quest Filtering - Math Subject", False, "Math filter returned non-Math quests")
                        return False
                    
                    if len(math_quests) != 4:
                        self.log_test("Quest Filtering - Math Count", False, f"Expected 4 Math quests, got {len(math_quests)}")
                        return False
                    
                    self.log_test("Quest Filtering - Math Subject", True, f"✅ Math subject filter working correctly ({len(math_quests)} quests)")
                else:
                    self.log_test("Quest Filtering - Math Subject", False, f"HTTP {response.status}")
                    return False
            
            return True
                    
        except Exception as e:
            self.log_test("Quest Filtering", False, f"Exception: {str(e)}")
            return False
    
    async def test_quest_submission_and_scoring(self):
        """Test quest submission, scoring, and XP calculation with expanded curriculum"""
        if not self.test_student_id:
            self.log_test("Quest Submission", False, "No test student ID available")
            return False
        
        try:
            # Get all quests to test different types
            async with self.session.get(f"{BACKEND_URL}/quests") as response:
                quests = await response.json()
                if not quests:
                    self.log_test("Quest Submission", False, "No quests available")
                    return False
                
                # Test Math quest (mango counting)
                math_quest = next((q for q in quests if "mango" in q["title"].lower()), None)
                if math_quest:
                    submission_data = {
                        "quest_id": math_quest["id"],
                        "answers": [
                            {
                                "question_id": "q1",
                                "answer": "15"  # Correct answer for mango counting
                            }
                        ]
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/students/{self.test_student_id}/submit_quest",
                        json=submission_data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            expected_fields = ["score", "xp_earned", "completed", "correct_answers", "total_questions"]
                            
                            if all(field in result for field in expected_fields):
                                if result["score"] == 100 and result["completed"] and result["xp_earned"] > 0:
                                    self.log_test("Quest Submission - Math Quest", True, 
                                                f"Math quest completed: Score: {result['score']}, XP: {result['xp_earned']}")
                                else:
                                    self.log_test("Quest Submission - Math Quest", False, 
                                                f"Unexpected scoring: {result}")
                                    return False
                            else:
                                self.log_test("Quest Submission - Math Quest", False, "Missing response fields")
                                return False
                        else:
                            error_text = await response.text()
                            self.log_test("Quest Submission - Math Quest", False, f"HTTP {response.status}: {error_text}")
                            return False
                
                # Test Social Studies quest (rivers)
                social_quest = next((q for q in quests if "river" in q["title"].lower()), None)
                if social_quest:
                    submission_data = {
                        "quest_id": social_quest["id"],
                        "answers": [
                            {
                                "question_id": "q1",
                                "answer": "Mahanadi"  # Correct answer for longest river in Odisha
                            }
                        ]
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/students/{self.test_student_id}/submit_quest",
                        json=submission_data,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result["score"] == 100 and result["completed"] and result["xp_earned"] > 0:
                                self.log_test("Quest Submission - Social Studies Quest", True, 
                                            f"Social Studies quest completed: Score: {result['score']}, XP: {result['xp_earned']}")
                            else:
                                self.log_test("Quest Submission - Social Studies Quest", False, 
                                            f"Unexpected scoring: {result}")
                                return False
                        else:
                            error_text = await response.text()
                            self.log_test("Quest Submission - Social Studies Quest", False, f"HTTP {response.status}: {error_text}")
                            return False
                
                # Test wrong answer handling
                if math_quest:
                    wrong_submission = {
                        "quest_id": math_quest["id"],
                        "answers": [
                            {
                                "question_id": "q1",
                                "answer": "10"  # Wrong answer
                            }
                        ]
                    }
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/students/{self.test_student_id}/submit_quest",
                        json=wrong_submission,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if result["score"] == 0 and not result["completed"]:
                                self.log_test("Quest Submission - Wrong Answer", True, 
                                            f"Correctly handled wrong answer: Score {result['score']}")
                                return True
                            else:
                                self.log_test("Quest Submission - Wrong Answer", False, 
                                            f"Wrong answer scoring issue: {result}")
                                return False
                        else:
                            self.log_test("Quest Submission - Wrong Answer", False, f"HTTP {response.status}")
                            return False
                        
        except Exception as e:
            self.log_test("Quest Submission", False, f"Exception: {str(e)}")
            return False
    
    async def test_progress_tracking(self):
        """Test progress tracking functionality"""
        if not self.test_student_id:
            self.log_test("Progress Tracking", False, "No test student ID available")
            return False
        
        try:
            async with self.session.get(f"{BACKEND_URL}/students/{self.test_student_id}/progress") as response:
                if response.status == 200:
                    progress_records = await response.json()
                    if len(progress_records) > 0:
                        # Check if progress record has required fields
                        record = progress_records[0]
                        required_fields = ["student_id", "quest_id", "completed", "score", "attempts", "xp_earned"]
                        
                        if all(field in record for field in required_fields):
                            self.log_test("Progress Tracking", True, 
                                        f"Found {len(progress_records)} progress records with complete data")
                            return True
                        else:
                            self.log_test("Progress Tracking", False, "Progress record missing required fields")
                            return False
                    else:
                        self.log_test("Progress Tracking", False, "No progress records found after quest submission")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Progress Tracking", False, f"HTTP {response.status}: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Progress Tracking", False, f"Exception: {str(e)}")
            return False
    
    async def test_gamification_system(self):
        """Test XP calculation, badges, and leaderboard"""
        try:
            # Test leaderboard
            async with self.session.get(f"{BACKEND_URL}/leaderboard") as response:
                if response.status == 200:
                    leaderboard = await response.json()
                    if isinstance(leaderboard, list):
                        if len(leaderboard) > 0:
                            # Check leaderboard entry structure
                            entry = leaderboard[0]
                            required_fields = ["rank", "name", "total_xp", "level", "avatar", "badges_count"]
                            
                            if all(field in entry for field in required_fields):
                                self.log_test("Gamification - Leaderboard", True, 
                                            f"Leaderboard working with {len(leaderboard)} entries")
                            else:
                                self.log_test("Gamification - Leaderboard", False, "Leaderboard entry missing fields")
                                return False
                        else:
                            self.log_test("Gamification - Leaderboard", True, "Empty leaderboard (expected for new system)")
                    else:
                        self.log_test("Gamification - Leaderboard", False, "Leaderboard not returning list")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Gamification - Leaderboard", False, f"HTTP {response.status}: {error_text}")
                    return False
            
            # Test badges system
            async with self.session.get(f"{BACKEND_URL}/badges") as response:
                if response.status == 200:
                    badges = await response.json()
                    expected_badges = ["first_quest", "math_wizard", "village_protector", "streak_master", "knowledge_seeker"]
                    
                    if all(badge in badges for badge in expected_badges):
                        # Check badge structure
                        first_badge = badges["first_quest"]
                        if "name" in first_badge and "name_odia" in first_badge and "icon" in first_badge:
                            self.log_test("Gamification - Badges", True, 
                                        f"All {len(expected_badges)} badges available with bilingual names")
                            return True
                        else:
                            self.log_test("Gamification - Badges", False, "Badge missing required fields")
                            return False
                    else:
                        self.log_test("Gamification - Badges", False, "Missing expected badges")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Gamification - Badges", False, f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("Gamification System", False, f"Exception: {str(e)}")
            return False
    
    async def test_ai_hint_generation(self):
        """Test AI-powered hint generation"""
        if not self.test_student_id:
            self.log_test("AI Hint Generation", False, "No test student ID available")
            return False
        
        try:
            # Get a quest first
            async with self.session.get(f"{BACKEND_URL}/quests?subject=math") as response:
                quests = await response.json()
                if not quests:
                    self.log_test("AI Hint Generation", False, "No quests available for hint testing")
                    return False
                
                quest = quests[0]
                quest_id = quest["id"]
                question_id = "q1"
                
                # Test hint generation
                hint_url = f"{BACKEND_URL}/students/{self.test_student_id}/generate_hint?quest_id={quest_id}&question_id={question_id}"
                
                async with self.session.post(hint_url) as response:
                    if response.status == 200:
                        hint_data = await response.json()
                        
                        if "hint" in hint_data and "hint_odia" in hint_data:
                            if hint_data["hint"] and hint_data["hint_odia"]:
                                self.log_test("AI Hint Generation", True, 
                                            f"Bilingual hints generated successfully")
                                return True
                            else:
                                self.log_test("AI Hint Generation", False, "Empty hint content")
                                return False
                        else:
                            self.log_test("AI Hint Generation", False, "Missing bilingual hint fields")
                            return False
                    else:
                        error_text = await response.text()
                        self.log_test("AI Hint Generation", False, f"HTTP {response.status}: {error_text}")
                        return False
                        
        except Exception as e:
            self.log_test("AI Hint Generation", False, f"Exception: {str(e)}")
            return False
    
    async def test_complete_student_journey(self):
        """Test complete student journey from registration to quest completion"""
        try:
            # Create a new student for journey testing
            journey_student = {
                "name": "Ravi Kumar",
                "age": 8,
                "grade": 2,
                "avatar": "warrior",
                "language": "odia"
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/students",
                json=journey_student,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_test("Complete Journey - Student Creation", False, f"HTTP {response.status}")
                    return False
                
                student_data = await response.json()
                journey_student_id = student_data["id"]
            
            # Get available quests
            async with self.session.get(f"{BACKEND_URL}/quests") as response:
                quests = await response.json()
                if not quests:
                    self.log_test("Complete Journey - Quest Retrieval", False, "No quests available")
                    return False
            
            # Complete a math quest
            math_quest = next((q for q in quests if q["subject"] == "math"), None)
            if not math_quest:
                self.log_test("Complete Journey - Math Quest", False, "No math quest found")
                return False
            
            submission = {
                "quest_id": math_quest["id"],
                "answers": [{"question_id": "q1", "answer": "5"}]
            }
            
            async with self.session.post(
                f"{BACKEND_URL}/students/{journey_student_id}/submit_quest",
                json=submission,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    self.log_test("Complete Journey - Quest Submission", False, f"HTTP {response.status}")
                    return False
                
                result = await response.json()
                if not result["completed"]:
                    self.log_test("Complete Journey - Quest Completion", False, "Quest not marked as completed")
                    return False
            
            # Check updated student profile
            async with self.session.get(f"{BACKEND_URL}/students/{journey_student_id}") as response:
                if response.status != 200:
                    self.log_test("Complete Journey - Profile Update", False, f"HTTP {response.status}")
                    return False
                
                updated_student = await response.json()
                if updated_student["total_xp"] > 0 and updated_student["level"] >= 1:
                    self.log_test("Complete Journey", True, 
                                f"Student journey completed: XP={updated_student['total_xp']}, Level={updated_student['level']}")
                    return True
                else:
                    self.log_test("Complete Journey", False, "Student stats not updated properly")
                    return False
                    
        except Exception as e:
            self.log_test("Complete Journey", False, f"Exception: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting EduQuest Odisha Backend API Tests")
        print(f"🌐 Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            # Core API tests
            await self.test_root_endpoint()
            await self.test_student_registration()
            await self.test_student_profile_retrieval()
            await self.test_quest_retrieval()
            await self.test_quest_submission_and_scoring()
            await self.test_progress_tracking()
            await self.test_gamification_system()
            await self.test_ai_hint_generation()
            await self.test_complete_student_journey()
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results["errors"]:
            print("\n🔍 FAILED TESTS:")
            for error in self.test_results["errors"]:
                print(f"  • {error}")
        
        success_rate = (self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed'])) * 100
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        return self.test_results['failed'] == 0

async def main():
    """Main test runner"""
    tester = EduQuestTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! EduQuest Odisha backend is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())