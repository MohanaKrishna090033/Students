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
    
    async def test_quest_retrieval(self):
        """Test quest retrieval with filters"""
        try:
            # Test all quests
            async with self.session.get(f"{BACKEND_URL}/quests") as response:
                if response.status == 200:
                    quests = await response.json()
                    if len(quests) >= 2:  # Should have at least the predefined quests
                        math_quest = next((q for q in quests if q["subject"] == "math"), None)
                        social_quest = next((q for q in quests if q["subject"] == "social_studies"), None)
                        
                        if math_quest and social_quest:
                            # Check bilingual content
                            if "title_odia" in math_quest and "description_odia" in math_quest:
                                self.log_test("Quest Retrieval - All Quests", True, f"Found {len(quests)} quests with bilingual content")
                            else:
                                self.log_test("Quest Retrieval - All Quests", False, "Missing bilingual content")
                                return False
                        else:
                            self.log_test("Quest Retrieval - All Quests", False, "Missing expected quest subjects")
                            return False
                    else:
                        self.log_test("Quest Retrieval - All Quests", False, f"Expected at least 2 quests, got {len(quests)}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("Quest Retrieval - All Quests", False, f"HTTP {response.status}: {error_text}")
                    return False
            
            # Test filtered by grade
            async with self.session.get(f"{BACKEND_URL}/quests?grade=1") as response:
                if response.status == 200:
                    grade_quests = await response.json()
                    if all(q["grade"] == 1 for q in grade_quests):
                        self.log_test("Quest Retrieval - Grade Filter", True, f"Grade 1 filter working, {len(grade_quests)} quests")
                    else:
                        self.log_test("Quest Retrieval - Grade Filter", False, "Grade filter not working properly")
                        return False
                else:
                    self.log_test("Quest Retrieval - Grade Filter", False, f"HTTP {response.status}")
                    return False
            
            # Test filtered by subject
            async with self.session.get(f"{BACKEND_URL}/quests?subject=math") as response:
                if response.status == 200:
                    math_quests = await response.json()
                    if all(q["subject"] == "math" for q in math_quests):
                        self.log_test("Quest Retrieval - Subject Filter", True, f"Math filter working, {len(math_quests)} quests")
                        return True
                    else:
                        self.log_test("Quest Retrieval - Subject Filter", False, "Subject filter not working properly")
                        return False
                else:
                    self.log_test("Quest Retrieval - Subject Filter", False, f"HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.log_test("Quest Retrieval", False, f"Exception: {str(e)}")
            return False
    
    async def test_quest_submission_and_scoring(self):
        """Test quest submission, scoring, and XP calculation"""
        if not self.test_student_id:
            self.log_test("Quest Submission", False, "No test student ID available")
            return False
        
        try:
            # First get a quest to submit
            async with self.session.get(f"{BACKEND_URL}/quests?subject=math") as response:
                quests = await response.json()
                if not quests:
                    self.log_test("Quest Submission", False, "No math quests available")
                    return False
                
                math_quest = quests[0]
                quest_id = math_quest["id"]
                
                # Submit correct answer
                submission_data = {
                    "quest_id": quest_id,
                    "answers": [
                        {
                            "question_id": "q1",
                            "answer": "5"  # Correct answer for mango counting
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
                                self.log_test("Quest Submission - Correct Answer", True, 
                                            f"Score: {result['score']}, XP: {result['xp_earned']}, Completed: {result['completed']}")
                            else:
                                self.log_test("Quest Submission - Correct Answer", False, 
                                            f"Unexpected scoring: {result}")
                                return False
                        else:
                            self.log_test("Quest Submission - Correct Answer", False, "Missing response fields")
                            return False
                    else:
                        error_text = await response.text()
                        self.log_test("Quest Submission - Correct Answer", False, f"HTTP {response.status}: {error_text}")
                        return False
                
                # Test incorrect answer
                wrong_submission = {
                    "quest_id": quest_id,
                    "answers": [
                        {
                            "question_id": "q1",
                            "answer": "3"  # Wrong answer
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