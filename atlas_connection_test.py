#!/usr/bin/env python3
"""
MongoDB Atlas Connection Fix Test
Focused test to verify the MongoDB Atlas SSL/TLS handshake fix is working.
Tests the exact scenario mentioned in the review request.
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://eduquest-village.preview.emergentagent.com/api"

class AtlasConnectionTester:
    def __init__(self):
        self.session = None
        self.test_student_id = None
        
    async def setup(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
    
    async def test_atlas_connection_fix(self):
        """Test the MongoDB Atlas connection fix with exact test data from review request"""
        print("🔍 Testing MongoDB Atlas Connection Fix")
        print("=" * 50)
        
        # Exact test data from review request
        test_data = {
            "name": "Test Student",
            "age": 7,
            "grade": 1, 
            "avatar": "boy",
            "language": "english"
        }
        
        print(f"📝 Using test data: {json.dumps(test_data, indent=2)}")
        print()
        
        # Step 1: Test POST /api/students endpoint
        print("Step 1: Testing POST /api/students endpoint...")
        try:
            async with self.session.post(
                f"{BACKEND_URL}/students",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    student_data = await response.json()
                    self.test_student_id = student_data.get("id")
                    print("✅ SUCCESS: Student creation successful!")
                    print(f"   Student ID: {self.test_student_id}")
                    print(f"   Student Name: {student_data.get('name')}")
                    print(f"   Student Grade: {student_data.get('grade')}")
                    print(f"   Total XP: {student_data.get('total_xp')}")
                    print(f"   Level: {student_data.get('level')}")
                    print()
                    
                    # Step 2: Test profile retrieval
                    print("Step 2: Testing profile retrieval...")
                    return await self.test_profile_retrieval()
                    
                else:
                    error_text = await response.text()
                    print(f"❌ FAILED: HTTP {response.status}")
                    print(f"   Error: {error_text}")
                    
                    # Check if it's the SSL handshake error
                    if "SSL" in error_text or "TLS" in error_text or "handshake" in error_text.lower():
                        print("🚨 CRITICAL: SSL/TLS handshake error still present!")
                        print("   The MongoDB Atlas connection fix is NOT working.")
                    else:
                        print("   Different error - not the SSL handshake issue.")
                    
                    return False
                    
        except Exception as e:
            error_str = str(e)
            print(f"❌ EXCEPTION: {error_str}")
            
            # Check if it's SSL/TLS related
            if any(keyword in error_str.lower() for keyword in ['ssl', 'tls', 'handshake', 'certificate']):
                print("🚨 CRITICAL: SSL/TLS connection error detected!")
                print("   The MongoDB Atlas connection fix is NOT working.")
            else:
                print("   Network or other connection error.")
            
            return False
    
    async def test_profile_retrieval(self):
        """Test profile retrieval to complete the basic flow"""
        if not self.test_student_id:
            print("❌ Cannot test profile retrieval - no student ID")
            return False
        
        try:
            async with self.session.get(f"{BACKEND_URL}/students/{self.test_student_id}") as response:
                print(f"Profile Retrieval Status: {response.status}")
                
                if response.status == 200:
                    profile_data = await response.json()
                    print("✅ SUCCESS: Profile retrieval successful!")
                    print(f"   Retrieved Name: {profile_data.get('name')}")
                    print(f"   Retrieved Grade: {profile_data.get('grade')}")
                    print(f"   Retrieved Avatar: {profile_data.get('avatar')}")
                    print()
                    
                    # Verify data matches
                    if (profile_data.get('name') == "Test Student" and 
                        profile_data.get('grade') == 1 and 
                        profile_data.get('avatar') == "boy"):
                        print("✅ SUCCESS: Profile data matches creation data!")
                        print("🎉 ATLAS CONNECTION FIX IS WORKING!")
                        print()
                        print("Summary:")
                        print("- Student creation: ✅ Working")
                        print("- Profile retrieval: ✅ Working") 
                        print("- Data persistence: ✅ Working")
                        print("- SSL/TLS handshake: ✅ Resolved")
                        return True
                    else:
                        print("❌ FAILED: Profile data mismatch")
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ FAILED: Profile retrieval HTTP {response.status}")
                    print(f"   Error: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ EXCEPTION during profile retrieval: {str(e)}")
            return False
    
    async def run_test(self):
        """Run the focused Atlas connection test"""
        print("🚀 MongoDB Atlas Connection Fix Test")
        print(f"🌐 Testing against: {BACKEND_URL}")
        print("=" * 60)
        
        await self.setup()
        
        try:
            success = await self.test_atlas_connection_fix()
            return success
        finally:
            await self.cleanup()

async def main():
    """Main test runner"""
    tester = AtlasConnectionTester()
    success = await tester.run_test()
    
    print("=" * 60)
    if success:
        print("🎉 ATLAS CONNECTION FIX VERIFIED!")
        print("The MongoDB Atlas SSL/TLS handshake error has been resolved.")
        print("Student creation and profile retrieval are working correctly.")
        sys.exit(0)
    else:
        print("⚠️  ATLAS CONNECTION FIX NOT WORKING")
        print("The SSL/TLS handshake error persists or other issues exist.")
        print("Further investigation needed.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())