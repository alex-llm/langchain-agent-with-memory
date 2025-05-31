"""
Memory Management Demo

This script demonstrates the new modular memory management system
for LangChain agents with advanced memory features.

Features demonstrated:
- Multiple memory storage types (in-memory vs file-based)
- Memory statistics and analysis
- Session management
- Memory export/import
- Memory cleanup and optimization
"""

import os
from dotenv import load_dotenv
from memory_manager import MemoryManager, create_memory_manager
from memory_tools import create_memory_tools, create_basic_memory_info_tool
from modern_langchain_demo import ModernMemoryAgent

# Load environment variables
load_dotenv()


def demo_memory_manager():
    """Demonstrate the memory manager functionality"""
    print("🧠 Memory Manager Demo")
    print("=" * 50)
    
    # Create different types of memory managers
    print("\n1. Creating Memory Managers:")
    
    # In-memory storage
    memory_manager = create_memory_manager(store_type="memory")
    print("✅ Created in-memory storage manager")
    
    # File-based storage
    file_memory_manager = create_memory_manager(
        store_type="file", 
        storage_dir="demo_memory_storage"
    )
    print("✅ Created file-based storage manager")
    
    # Test basic memory operations
    print("\n2. Testing Basic Memory Operations:")
    
    # Add some test messages
    session_id = "demo_session"
    history = memory_manager.get_session_history(session_id)
    
    from langchain_core.messages import HumanMessage, AIMessage
    history.add_message(HumanMessage(content="Hello, I'm testing the memory system"))
    history.add_message(AIMessage(content="Great! I can remember our conversation."))
    history.add_message(HumanMessage(content="What's 2 + 2?"))
    history.add_message(AIMessage(content="2 + 2 = 4"))
    
    # Get memory statistics
    stats = memory_manager.get_memory_stats(session_id)
    print(f"📊 Memory Stats: {stats.message_count} messages, {stats.total_tokens} tokens")
    
    # Test memory summary
    summary = memory_manager.get_memory_summary()
    print(f"📈 Memory Summary: {summary['total_sessions']} sessions, {summary['total_messages']} total messages")
    
    # Test export/import
    print("\n3. Testing Export/Import:")
    exported_data = memory_manager.export_session(session_id)
    print(f"📤 Exported {len(exported_data)} characters of data")
    
    # Import to a new session
    new_session_id = "imported_session"
    success = memory_manager.import_session(new_session_id, exported_data)
    print(f"📥 Import success: {success}")
    
    # Verify import
    imported_stats = memory_manager.get_memory_stats(new_session_id)
    print(f"📊 Imported Stats: {imported_stats.message_count} messages")
    
    print("\n4. Testing Session Management:")
    
    # List all sessions
    sessions = memory_manager.get_all_sessions()
    print(f"📋 Available sessions: {sessions}")
    
    # Clear a session
    memory_manager.clear_session(session_id)
    cleared_stats = memory_manager.get_memory_stats(session_id)
    print(f"🧹 After clearing: {cleared_stats.message_count} messages")
    
    print("\n✅ Memory Manager Demo Complete!")


def demo_memory_tools():
    """Demonstrate the memory tools functionality"""
    print("\n🔧 Memory Tools Demo")
    print("=" * 50)
    
    # Create memory manager and tools
    memory_manager = create_memory_manager(store_type="memory")
    memory_tools = create_memory_tools(memory_manager)
    
    print(f"🛠️ Created {len(memory_tools)} memory tools:")
    for i, tool in enumerate(memory_tools, 1):
        print(f"  {i}. {tool.name}: {tool.description}")
    
    # Add some test data
    session_id = "tools_demo"
    history = memory_manager.get_session_history(session_id)
    
    from langchain_core.messages import HumanMessage, AIMessage
    for i in range(5):
        history.add_message(HumanMessage(content=f"Test message {i+1}"))
        history.add_message(AIMessage(content=f"Response to message {i+1}"))
    
    # Test some tools
    print("\n🧪 Testing Memory Tools:")
    
    # Test memory stats tool
    stats_tool = memory_tools[0]  # get_memory_stats
    result = stats_tool.invoke({"session_id": session_id})
    print(f"📊 Stats Tool Result:\n{result}")
    
    # Test sessions list tool
    sessions_tool = memory_tools[1]  # get_all_sessions
    result = sessions_tool.invoke({})
    print(f"\n📋 Sessions Tool Result:\n{result}")
    
    # Test memory summary tool
    summary_tool = memory_tools[6]  # get_memory_summary
    result = summary_tool.invoke({})
    print(f"\n📈 Summary Tool Result:\n{result}")
    
    print("\n✅ Memory Tools Demo Complete!")


def demo_agent_with_memory():
    """Demonstrate agent with enhanced memory system"""
    print("\n🤖 Agent with Enhanced Memory Demo")
    print("=" * 50)
    
    # Check if API is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ No API key found. Skipping agent demo.")
        print("Set OPENAI_API_KEY environment variable to test agent functionality.")
        return
    
    # Create agent with enhanced memory
    agent = ModernMemoryAgent()
    
    if not agent.api_available:
        print("⚠️ Agent API not available. Skipping agent demo.")
        return
    
    print("✅ Created agent with enhanced memory system")
    
    # Test conversation with memory
    session_id = "enhanced_demo"
    
    print("\n💬 Testing Conversation with Memory:")
    
    # First message
    response1 = agent.chat("Hi, my name is Alice and I like programming", session_id)
    print(f"User: Hi, my name is Alice and I like programming")
    print(f"Agent: {response1}")
    
    # Second message - test memory recall
    response2 = agent.chat("What's my name and what do I like?", session_id)
    print(f"\nUser: What's my name and what do I like?")
    print(f"Agent: {response2}")
    
    # Test memory info tool
    response3 = agent.chat("How many messages do we have in our conversation?", session_id)
    print(f"\nUser: How many messages do we have in our conversation?")
    print(f"Agent: {response3}")
    
    # Show memory details
    memory_details = agent.show_memory(session_id)
    print(f"\n📝 Memory Details:\n{memory_details}")
    
    print("\n✅ Agent with Enhanced Memory Demo Complete!")


def main():
    """Run all memory demos"""
    print("🧠 Modular Memory System Demo")
    print("=" * 60)
    print("Demonstrating the new centralized memory management system")
    print("for LangChain agents with advanced features.")
    print()
    
    try:
        # Demo 1: Memory Manager
        demo_memory_manager()
        
        # Demo 2: Memory Tools
        demo_memory_tools()
        
        # Demo 3: Agent with Enhanced Memory
        demo_agent_with_memory()
        
        print("\n🎉 All Memory Demos Complete!")
        print("\nKey Benefits of the New Memory System:")
        print("✅ Centralized memory management")
        print("✅ Multiple storage backends (memory/file)")
        print("✅ Advanced memory statistics and analysis")
        print("✅ Session management and cleanup")
        print("✅ Export/import functionality")
        print("✅ Modular and extensible design")
        print("✅ Easy integration with existing agents")
        
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()