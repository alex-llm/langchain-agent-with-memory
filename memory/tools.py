"""
Memory Tools Module for LangChain Agent

This module provides memory-related tools that can be used by LangChain agents
to manage, analyze, and interact with conversation memory.

Features:
- Memory statistics and analysis tools
- Session management tools
- Memory export/import tools
- Memory cleanup and optimization tools
"""

from typing import Dict, List, Any, Optional
from langchain_core.tools import tool
from .manager import MemoryManager
import json
import datetime


class MemoryTools:
    """Collection of memory-related tools for LangChain agents"""
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize memory tools with a memory manager instance
        
        Args:
            memory_manager: The memory manager instance to use
        """
        self.memory_manager = memory_manager
    
    def get_tools(self) -> List:
        """Get all memory-related tools"""
        return [
            self.get_memory_stats_tool(),
            self.get_all_sessions_tool(),
            self.clear_session_tool(),
            self.export_session_tool(),
            self.import_session_tool(),
            self.cleanup_old_sessions_tool(),
            self.get_memory_summary_tool(),
            self.trim_session_messages_tool()
        ]
    
    def get_memory_stats_tool(self):
        """Tool to get memory statistics for a session"""
        @tool
        def get_memory_stats(session_id: str = "default") -> str:
            """Get detailed memory statistics for a specific session."""
            try:
                stats = self.memory_manager.get_memory_stats(session_id)
                
                result = f"📊 Memory Statistics for Session '{session_id}':\n"
                result += f"• Messages: {stats.message_count}\n"
                result += f"• Tokens: {stats.total_tokens}\n"
                result += f"• Memory Size: {stats.memory_size_bytes} bytes\n"
                
                if stats.first_message_time:
                    result += f"• First Message: {stats.first_message_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                if stats.last_message_time:
                    result += f"• Last Message: {stats.last_message_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                return result
            except Exception as e:
                return f"Error getting memory stats: {str(e)}"
        
        return get_memory_stats
    
    def get_all_sessions_tool(self):
        """Tool to get all available sessions"""
        @tool
        def get_all_sessions() -> str:
            """Get a list of all available conversation sessions."""
            try:
                sessions = self.memory_manager.get_all_sessions()
                
                if not sessions:
                    return "No conversation sessions found."
                
                result = f"📋 Available Sessions ({len(sessions)} total):\n"
                for i, session_id in enumerate(sessions, 1):
                    stats = self.memory_manager.get_memory_stats(session_id)
                    result += f"{i}. '{session_id}' - {stats.message_count} messages\n"
                
                return result
            except Exception as e:
                return f"Error getting sessions: {str(e)}"
        
        return get_all_sessions
    
    def clear_session_tool(self):
        """Tool to clear a specific session"""
        @tool
        def clear_session(session_id: str) -> str:
            """Clear all conversation history for a specific session."""
            try:
                success = self.memory_manager.clear_session(session_id)
                if success:
                    return f"✅ Successfully cleared session '{session_id}'"
                else:
                    return f"❌ Failed to clear session '{session_id}'"
            except Exception as e:
                return f"Error clearing session: {str(e)}"
        
        return clear_session
    
    def export_session_tool(self):
        """Tool to export session data"""
        @tool
        def export_session(session_id: str, format: str = "json") -> str:
            """Export conversation data from a session in JSON format."""
            try:
                exported_data = self.memory_manager.export_session(session_id, format)
                
                # For display purposes, show a summary instead of full data
                import json
                data = json.loads(exported_data)
                stats = data.get("stats", {})
                message_count = stats.get("message_count", 0)
                
                result = f"📤 Exported session '{session_id}':\n"
                result += f"• Format: {format.upper()}\n"
                result += f"• Messages: {message_count}\n"
                result += f"• Data size: {len(exported_data)} characters\n"
                result += "\n💾 Export data (first 200 chars):\n"
                result += exported_data[:200] + "..." if len(exported_data) > 200 else exported_data
                
                return result
            except Exception as e:
                return f"Error exporting session: {str(e)}"
        
        return export_session
    
    def import_session_tool(self):
        """Tool to import session data"""
        @tool
        def import_session(session_id: str, data: str, format: str = "json") -> str:
            """Import conversation data into a session from JSON format."""
            try:
                success = self.memory_manager.import_session(session_id, data, format)
                if success:
                    stats = self.memory_manager.get_memory_stats(session_id)
                    return f"✅ Successfully imported data into session '{session_id}'\n• Messages imported: {stats.message_count}"
                else:
                    return f"❌ Failed to import data into session '{session_id}'"
            except Exception as e:
                return f"Error importing session: {str(e)}"
        
        return import_session
    
    def cleanup_old_sessions_tool(self):
        """Tool to cleanup old sessions"""
        @tool
        def cleanup_old_sessions(days_old: int = 30) -> str:
            """Clean up conversation sessions older than specified number of days."""
            try:
                cleaned_count = self.memory_manager.cleanup_old_sessions(days_old)
                return f"🧹 Cleaned up {cleaned_count} sessions older than {days_old} days"
            except Exception as e:
                return f"Error cleaning up sessions: {str(e)}"
        
        return cleanup_old_sessions
    
    def get_memory_summary_tool(self):
        """Tool to get overall memory summary"""
        @tool
        def get_memory_summary() -> str:
            """Get an overall summary of memory usage across all sessions."""
            try:
                summary = self.memory_manager.get_memory_summary()
                
                result = "📈 Overall Memory Summary:\n"
                result += f"• Total Sessions: {summary['total_sessions']}\n"
                result += f"• Total Messages: {summary['total_messages']}\n"
                result += f"• Total Memory: {summary['total_memory_bytes']} bytes\n"
                result += f"• Average Messages/Session: {summary['average_messages_per_session']}\n"
                
                if summary['total_sessions'] > 0:
                    result += "\n📊 Session Details:\n"
                    for session_data in summary['sessions'][:5]:  # Show first 5 sessions
                        result += f"• '{session_data['session_id']}': {session_data['message_count']} messages\n"
                    
                    if summary['total_sessions'] > 5:
                        result += f"... and {summary['total_sessions'] - 5} more sessions\n"
                
                return result
            except Exception as e:
                return f"Error getting memory summary: {str(e)}"
        
        return get_memory_summary
    
    def trim_session_messages_tool(self):
        """Tool to trim session messages"""
        @tool
        def trim_session_messages(session_id: str, max_messages: int = 100) -> str:
            """Trim a session to keep only the most recent messages."""
            try:
                removed_count = self.memory_manager.trim_session_messages(session_id, max_messages)
                if removed_count > 0:
                    return f"✂️ Trimmed {removed_count} old messages from session '{session_id}', keeping {max_messages} most recent"
                else:
                    return f"ℹ️ Session '{session_id}' already has {max_messages} or fewer messages"
            except Exception as e:
                return f"Error trimming session: {str(e)}"
        
        return trim_session_messages


def create_memory_tools(memory_manager: MemoryManager) -> List:
    """
    Create memory tools for a given memory manager
    
    Args:
        memory_manager: The memory manager instance
        
    Returns:
        List of memory-related tools
    """
    memory_tools = MemoryTools(memory_manager)
    return memory_tools.get_tools()


# Convenience function for creating basic memory info tool
def create_basic_memory_info_tool(memory_manager: MemoryManager):
    """Create a basic memory info tool"""
    @tool
    def memory_info(session_id: str = "default") -> str:
        """Get basic information about conversation memory."""
        try:
            stats = memory_manager.get_memory_stats(session_id)
            return f"Memory contains {stats.message_count} messages, {stats.total_tokens} tokens, {stats.memory_size_bytes} bytes"
        except Exception as e:
            return f"Error getting memory info: {str(e)}"
    
    return memory_info 