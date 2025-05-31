#!/usr/bin/env python3
"""
Memory System Test Script

This script tests the modular memory management system without requiring API keys.
It verifies all core functionality including memory managers, tools, and storage backends.
"""

import os
import tempfile
import shutil
from datetime import datetime, timedelta

from memory_manager import (
    MemoryManager, 
    create_memory_manager, 
    InMemoryStore, 
    FileBasedMemoryStore,
    MemoryStats
)
from memory_tools import create_memory_tools, create_basic_memory_info_tool
from langchain_core.messages import HumanMessage, AIMessage


def test_memory_manager_basic():
    """Test basic memory manager functionality"""
    print("🧪 Testing Memory Manager Basic Functionality")
    print("-" * 50)
    
    # Test in-memory storage
    memory_manager = create_memory_manager(store_type="memory")
    session_id = "test_session"
    
    # Add some messages
    history = memory_manager.get_session_history(session_id)
    history.add_message(HumanMessage(content="Hello"))
    history.add_message(AIMessage(content="Hi there!"))
    history.add_message(HumanMessage(content="How are you?"))
    history.add_message(AIMessage(content="I'm doing well, thank you!"))
    
    # Test statistics
    stats = memory_manager.get_memory_stats(session_id)
    assert stats.message_count == 4, f"Expected 4 messages, got {stats.message_count}"
    assert stats.session_id == session_id, f"Session ID mismatch"
    
    # Test session listing
    sessions = memory_manager.get_all_sessions()
    assert session_id in sessions, f"Session {session_id} not found in {sessions}"
    
    # Test memory summary
    summary = memory_manager.get_memory_summary()
    assert summary['total_sessions'] == 1, f"Expected 1 session, got {summary['total_sessions']}"
    assert summary['total_messages'] == 4, f"Expected 4 messages, got {summary['total_messages']}"
    
    print("✅ In-memory storage tests passed")
    
    # Test clearing session
    memory_manager.clear_session(session_id)
    cleared_stats = memory_manager.get_memory_stats(session_id)
    assert cleared_stats.message_count == 0, f"Expected 0 messages after clear, got {cleared_stats.message_count}"
    
    print("✅ Session clearing tests passed")


def test_file_based_storage():
    """Test file-based storage functionality"""
    print("\n🧪 Testing File-Based Storage")
    print("-" * 50)
    
    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp(prefix="memory_test_")
    
    try:
        # Create file-based memory manager
        file_manager = create_memory_manager(
            store_type="file", 
            storage_dir=temp_dir
        )
        
        session_id = "file_test_session"
        
        # Add messages
        history = file_manager.get_session_history(session_id)
        history.add_message(HumanMessage(content="Testing file storage"))
        history.add_message(AIMessage(content="File storage is working!"))
        
        # Save session
        file_manager.save_all_sessions()
        
        # Create new manager with same directory to test persistence
        file_manager2 = create_memory_manager(
            store_type="file", 
            storage_dir=temp_dir
        )
        
        # Check if data persisted
        history2 = file_manager2.get_session_history(session_id)
        assert len(history2.messages) == 2, f"Expected 2 persisted messages, got {len(history2.messages)}"
        
        stats = file_manager2.get_memory_stats(session_id)
        assert stats.message_count == 2, f"Expected 2 messages in stats, got {stats.message_count}"
        
        print("✅ File persistence tests passed")
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_export_import():
    """Test export/import functionality"""
    print("\n🧪 Testing Export/Import Functionality")
    print("-" * 50)
    
    memory_manager = create_memory_manager(store_type="memory")
    
    # Create source session
    source_session = "source_session"
    history = memory_manager.get_session_history(source_session)
    history.add_message(HumanMessage(content="Export test message"))
    history.add_message(AIMessage(content="This will be exported"))
    
    # Export session
    exported_data = memory_manager.export_session(source_session, format="json")
    assert len(exported_data) > 0, "Export data should not be empty"
    
    # Import to new session
    target_session = "imported_session"
    success = memory_manager.import_session(target_session, exported_data, format="json")
    assert success, "Import should succeed"
    
    # Verify imported data
    imported_stats = memory_manager.get_memory_stats(target_session)
    original_stats = memory_manager.get_memory_stats(source_session)
    
    assert imported_stats.message_count == original_stats.message_count, \
        f"Message count mismatch: {imported_stats.message_count} vs {original_stats.message_count}"
    
    print("✅ Export/import tests passed")


def test_memory_tools():
    """Test memory tools functionality"""
    print("\n🧪 Testing Memory Tools")
    print("-" * 50)
    
    memory_manager = create_memory_manager(store_type="memory")
    
    # Create test data
    session_id = "tools_test_session"
    history = memory_manager.get_session_history(session_id)
    for i in range(5):
        history.add_message(HumanMessage(content=f"Test message {i+1}"))
        history.add_message(AIMessage(content=f"Response {i+1}"))
    
    # Create memory tools
    memory_tools = create_memory_tools(memory_manager)
    assert len(memory_tools) == 8, f"Expected 8 memory tools, got {len(memory_tools)}"
    
    # Test get_memory_stats tool
    stats_tool = memory_tools[0]
    result = stats_tool.invoke({"session_id": session_id})
    assert "10" in result, f"Expected message count in result: {result}"
    
    # Test get_all_sessions tool
    sessions_tool = memory_tools[1]
    result = sessions_tool.invoke({})
    assert session_id in result, f"Expected session ID in result: {result}"
    
    # Test memory summary tool
    summary_tool = memory_tools[6]
    result = summary_tool.invoke({})
    assert "Total Sessions: 1" in result, f"Expected session count in summary: {result}"
    
    print("✅ Memory tools tests passed")


def test_session_management():
    """Test advanced session management features"""
    print("\n🧪 Testing Session Management")
    print("-" * 50)
    
    memory_manager = create_memory_manager(store_type="memory")
    
    # Create multiple sessions
    sessions = ["session1", "session2", "session3"]
    for session_id in sessions:
        history = memory_manager.get_session_history(session_id)
        history.add_message(HumanMessage(content=f"Message in {session_id}"))
        history.add_message(AIMessage(content=f"Response in {session_id}"))
    
    # Test get all sessions
    all_sessions = memory_manager.get_all_sessions()
    for session_id in sessions:
        assert session_id in all_sessions, f"Session {session_id} not found"
    
    # Test clear all sessions
    cleared_count = memory_manager.clear_all_sessions()
    assert cleared_count == len(sessions), f"Expected {len(sessions)} cleared, got {cleared_count}"
    
    # Verify all sessions are cleared
    for session_id in sessions:
        stats = memory_manager.get_memory_stats(session_id)
        assert stats.message_count == 0, f"Session {session_id} should be empty"
    
    print("✅ Session management tests passed")


def test_message_trimming():
    """Test message trimming functionality"""
    print("\n🧪 Testing Message Trimming")
    print("-" * 50)
    
    memory_manager = create_memory_manager(store_type="memory", max_messages_per_session=100)
    session_id = "trim_test_session"
    
    # Add many messages
    history = memory_manager.get_session_history(session_id)
    for i in range(20):
        history.add_message(HumanMessage(content=f"Message {i+1}"))
        history.add_message(AIMessage(content=f"Response {i+1}"))
    
    # Verify we have 40 messages
    stats = memory_manager.get_memory_stats(session_id)
    assert stats.message_count == 40, f"Expected 40 messages, got {stats.message_count}"
    
    # Trim to 10 messages
    trimmed_count = memory_manager.trim_session_messages(session_id, max_messages=10)
    assert trimmed_count == 30, f"Expected 30 messages trimmed, got {trimmed_count}"
    
    # Verify trimming worked
    stats_after = memory_manager.get_memory_stats(session_id)
    assert stats_after.message_count == 10, f"Expected 10 messages after trim, got {stats_after.message_count}"
    
    print("✅ Message trimming tests passed")


def run_all_tests():
    """Run all memory system tests"""
    print("🧠 Memory System Comprehensive Test Suite")
    print("=" * 60)
    print("Testing the modular memory management system...")
    print()
    
    try:
        test_memory_manager_basic()
        test_file_based_storage()
        test_export_import()
        test_memory_tools()
        test_session_management()
        test_message_trimming()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("✅ The memory system is working correctly")
        print("✅ All core functionality verified")
        print("✅ Both storage backends tested")
        print("✅ Memory tools functioning properly")
        print("✅ Session management working")
        print("✅ Export/import functionality verified")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("Please check the error and fix the issue.")
        raise


if __name__ == "__main__":
    run_all_tests() 