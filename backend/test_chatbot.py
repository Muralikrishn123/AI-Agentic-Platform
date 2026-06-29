"""Test script for verifying chatbot LLM responses and context generation."""
import sys
import os

# Ensure the app path is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Apply Python 3.14 and gRPC workarounds first
import app.patch

import asyncio
from app.database.connection import connect_to_mongo, close_mongo_connection
from app.api.chatbot import ChatbotQueryRequest, query_chatbot

async def test_chatbot():
    print("Initializing Database Connection...")
    await connect_to_mongo()
    
    try:
        # Test 1: General Help Query
        print("\n--- Test 1: Chatbot Route Verification ---")
        request_obj = ChatbotQueryRequest(query="How do I create a custom plugin?")
        result = await query_chatbot(request_obj, current_user={})
        print(f"Chatbot response success status: {result.get('success')}")
        print(f"Reply:\n{result.get('response')}")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_chatbot())
