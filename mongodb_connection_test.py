#!/usr/bin/env python3
"""
MongoDB Connection Fix Test
Tests the specific MongoDB connection fix by switching from Atlas to local MongoDB
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://eduquest-village.preview.emergentagent.com/api"

class MongoDBConnectionTester:
    def __init__(self):
        self.session = None
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
    
    async def test_mongodb_connection_fix(self):
        """Test the MongoDB connection fix with exact review request data"""
        # Exact test data from review request
        test_data = {
            "name": "Test Student", 
            "age": 7,
            "grade": 1,
            "avatar": "boy",
            "language": "english"
        }
        
        print(f"🔍 Testing MongoDB connection fix with data: {test_data}")
        
        try:
            # Test POST /api/students endpoint
            async with self.session.post(
                f"{BACKEND_URL}/students",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                print(f"📡 POST /api/students response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📄 Response data: {json.dumps(data, indent=2)}")
                    
                    # Verify all required fields are present
                    required_fields = ["id", "name", "age", "grade", "avatar", "language", "total_xp", "level"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        student_id = data["id"]
                        self.log_test("MongoDB Connection - Student Creation", True, 
                                    f"Student created successfully with ID: {student_id}")
                        
                        # Test profile retrieval to complete the flow
                        return await self.test_profile_retrieval(student_id)
                    else:
                        self.log_test("MongoDB Connection - Student Creation", False, 
                                    f"Missing required fields: {missing_fields}")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("MongoDB Connection - Student Creation", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("MongoDB Connection - Student Creation", False, f"Exception: {str(e)}")
            return False
    
    async def test_profile_retrieval(self, student_id: str):
        """Test profile retrieval to verify complete flow"""
        try:
            async with self.session.get(f"{BACKEND_URL}/students/{student_id}") as response:
                print(f"📡 GET /api/students/{student_id} response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"📄 Profile data: {json.dumps(data, indent=2)}")
                    
                    # Verify the data matches what we created
                    if (data["name"] == "Test Student" and 
                        data["age"] == 7 and 
                        data["grade"] == 1 and 
                        data["avatar"] == "boy" and 
                        data["language"] == "english"):
                        
                        self.log_test("MongoDB Connection - Profile Retrieval", True, 
                                    "Profile data matches creation data perfectly")
                        return True
                    else:
                        self.log_test("MongoDB Connection - Profile Retrieval", False, 
                                    "Profile data does not match creation data")
                        return False
                else:
                    error_text = await response.text()
                    self.log_test("MongoDB Connection - Profile Retrieval", False, 
                                f"HTTP {response.status}: {error_text}")
                    return False
                    
        except Exception as e:
            self.log_test("MongoDB Connection - Profile Retrieval", False, f"Exception: {str(e)}")
            return False
    
    async def run_mongodb_test(self):
        """Run the MongoDB connection fix test"""
        print("🔧 Testing MongoDB Connection Fix")
        print("📋 Switching from MongoDB Atlas to Local MongoDB")
        print(f"🌐 Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            success = await self.test_mongodb_connection_fix()
            
        finally:
            await self.cleanup()
        
        # Print summary
        print("=" * 60)
        print("📊 MONGODB CONNECTION TEST SUMMARY")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        if self.test_results["errors"]:
            print("\n🔍 FAILED TESTS:")
            for error in self.test_results["errors"]:
                print(f"  • {error}")
        
        if success:
            print("\n🎉 MongoDB connection fix SUCCESSFUL!")
            print("✅ Student creation and profile retrieval working without SSL/TLS errors")
        else:
            print("\n⚠️  MongoDB connection fix FAILED!")
            print("❌ SSL/TLS errors may still be present")
        
        return success

async def main():
    """Main test runner"""
    tester = MongoDBConnectionTester()
    success = await tester.run_mongodb_test()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())