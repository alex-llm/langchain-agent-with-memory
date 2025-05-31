#!/usr/bin/env python3
"""
Debug ModernMemoryAgent initialization

This script helps diagnose issues with agent initialization
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Debugging ModernMemoryAgent Initialization")
print("=" * 60)

print("1. Environment Variables:")
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
print(f"   API Key: {'Set' if api_key else 'Not set'}")
print(f"   API Base: {api_base}")

print("\n2. Creating ModernMemoryAgent:")
try:
    from modern_langchain_demo import ModernMemoryAgent
    
    print("   Creating agent instance...")
    agent = ModernMemoryAgent()
    
    print("   Checking agent attributes:")
    print(f"   - api_available: {getattr(agent, 'api_available', 'Not set')}")
    print(f"   - api_key: {'Set' if getattr(agent, 'api_key', None) else 'Not set'}")
    print(f"   - api_base: {getattr(agent, 'api_base', 'Not set')}")
    print(f"   - memory_manager: {'Present' if hasattr(agent, 'memory_manager') else 'Missing'}")
    print(f"   - agent_with_chat_history: {'Present' if hasattr(agent, 'agent_with_chat_history') else 'Missing'}")
    print(f"   - tools: {'Present' if hasattr(agent, 'tools') else 'Missing'}")
    
    if hasattr(agent, 'tools'):
        print(f"   - tools count: {len(agent.tools) if agent.tools else 0}")
    
    if hasattr(agent, 'memory_manager'):
        print("\n   Memory manager test:")
        session_id = "debug_test"
        history = agent.memory_manager.get_session_history(session_id)
        print(f"   - Session history created: {history is not None}")
        
        # Test memory functionality
        from langchain_core.messages import HumanMessage, AIMessage
        history.add_message(HumanMessage(content="Test message"))
        stats = agent.memory_manager.get_memory_stats(session_id)
        print(f"   - Memory stats: {stats.message_count} messages")
    
    print("\n✅ Agent debugging complete!")
    
except Exception as e:
    print(f"\n❌ Error during agent creation: {str(e)}")
    import traceback
    traceback.print_exc() 