#!/usr/bin/env python3
"""
Environment Variables Test

Test if .env file is correctly loaded
"""

import os
from dotenv import load_dotenv

print("🔍 Environment Variables Test")
print("=" * 50)

print("1. Before loading .env:")
print(f"   OPENAI_API_KEY: {'Set' if os.getenv('OPENAI_API_KEY') else 'Not set'}")
print(f"   OPENAI_API_BASE: {os.getenv('OPENAI_API_BASE', 'Not set')}")

print("\n2. Loading .env file...")
result = load_dotenv()
print(f"   load_dotenv() result: {result}")

print("\n3. After loading .env:")
api_key = os.getenv('OPENAI_API_KEY')
api_base = os.getenv('OPENAI_API_BASE')

print(f"   OPENAI_API_KEY: {'Set' if api_key else 'Not set'}")
if api_key:
    print(f"   API Key length: {len(api_key)}")
    print(f"   API Key starts with: {api_key[:10]}...")

print(f"   OPENAI_API_BASE: {api_base}")

print("\n4. Testing ModernMemoryAgent initialization:")
try:
    from modern_langchain_demo import ModernMemoryAgent
    agent = ModernMemoryAgent()
    
    print(f"   Agent API available: {agent.api_available}")
    if hasattr(agent, 'api_key'):
        print(f"   Agent has API key: {'Yes' if agent.api_key else 'No'}")
    if hasattr(agent, 'api_base'):
        print(f"   Agent API base: {agent.api_base}")
        
except Exception as e:
    print(f"   Error creating agent: {str(e)}")

print("\n✅ Environment test complete!") 