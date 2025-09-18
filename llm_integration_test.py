#!/usr/bin/env python3
"""
Test Multi-LLM Integration specifically
"""

import asyncio
import aiohttp
import json

BACKEND_URL = "https://eduquest-village.preview.emergentagent.com/api"

async def test_llm_integration():
    """Test the multi-LLM integration with different providers"""
    async with aiohttp.ClientSession() as session:
        # Create a test student
        student_data = {
            "name": "Test Student",
            "age": 7,
            "grade": 1,
            "avatar": "student",
            "language": "english"
        }
        
        async with session.post(f"{BACKEND_URL}/students", json=student_data) as response:
            student = await response.json()
            student_id = student["id"]
        
        # Get a quest
        async with session.get(f"{BACKEND_URL}/quests?subject=math") as response:
            quests = await response.json()
            quest_id = quests[0]["id"]
        
        # Test hint generation multiple times to see different LLM responses
        for i in range(3):
            hint_url = f"{BACKEND_URL}/students/{student_id}/generate_hint?quest_id={quest_id}&question_id=q1"
            
            async with session.post(hint_url) as response:
                if response.status == 200:
                    hint_data = await response.json()
                    print(f"Hint {i+1}:")
                    print(f"  English: {hint_data['hint']}")
                    print(f"  Odia: {hint_data['hint_odia']}")
                    print()
                else:
                    print(f"Hint {i+1} failed: HTTP {response.status}")

if __name__ == "__main__":
    asyncio.run(test_llm_integration())