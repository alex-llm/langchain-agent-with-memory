"""
Memory Tools Module

Provides memory management tools for LangChain agents:
- Memory Statistics: Get detailed memory usage information
- Session Management: Manage conversation sessions
- Memory Export/Import: Backup and restore conversation data
- Memory Cleanup: Optimize and clean old data
"""

from typing import Dict, List
from langchain_core.tools import tool
import json
import datetime

from .registry import BaseToolModule, ToolConfig, ToolCategory


class MemoryToolsModule(BaseToolModule):
    """Module containing memory management tools"""
    
    def __init__(self, memory_manager=None, enable_user_approval=False):
        super().__init__(memory_manager, enable_user_approval)
        if not memory_manager:
            raise ValueError("MemoryToolsModule requires a memory_manager instance")
    
    def get_tools(self) -> List:
        """Get all memory management tools"""
        return [
            self._create_memory_info_tool(),
            self._create_memory_stats_tool(),
            self._create_all_sessions_tool(),
            self._create_clear_session_tool(),
            self._create_export_session_tool(),
            self._create_import_session_tool(),
            self._create_cleanup_sessions_tool(),
            self._create_memory_summary_tool(),
            self._create_trim_session_tool()
        ]
    
    def get_tool_configs(self) -> Dict[str, ToolConfig]:
        """Get tool configurations for memory tools"""
        return {
            "memory_info": ToolConfig(
                name="memory_info",
                category=ToolCategory.MEMORY,
                description="Get basic information about conversation memory",
                requires_approval=False,
                risk_level="low",
                example_usage="How many messages do we have?",
                parameters={"session_id": "Session ID (default: 'default')"},
                tags=["memory", "statistics", "information"]
            ),
            "get_memory_stats": ToolConfig(
                name="get_memory_stats",
                category=ToolCategory.MEMORY,
                description="Get detailed memory statistics for a session",
                requires_approval=False,
                risk_level="low",
                example_usage="Show detailed memory stats",
                parameters={"session_id": "Session ID (default: 'default')"},
                tags=["memory", "statistics", "detailed", "analysis"]
            ),
            "get_all_sessions": ToolConfig(
                name="get_all_sessions",
                category=ToolCategory.MEMORY,
                description="Get a list of all available conversation sessions",
                requires_approval=False,
                risk_level="low",
                example_usage="List all conversation sessions",
                parameters={},
                tags=["memory", "sessions", "list", "management"]
            ),
            "clear_session": ToolConfig(
                name="clear_session",
                category=ToolCategory.MEMORY,
                description="Clear all conversation history for a specific session",
                requires_approval=True,
                risk_level="medium",
                example_usage="Clear conversation history",
                parameters={"session_id": "Session ID to clear"},
                tags=["memory", "clear", "delete", "cleanup"]
            ),
            "export_session": ToolConfig(
                name="export_session",
                category=ToolCategory.MEMORY,
                description="Export conversation data from a session",
                requires_approval=False,
                risk_level="low",
                example_usage="Export my conversation history",
                parameters={
                    "session_id": "Session ID to export", 
                    "format": "Export format (default: 'json')"
                },
                tags=["memory", "export", "backup", "data"]
            ),
            "import_session": ToolConfig(
                name="import_session",
                category=ToolCategory.MEMORY,
                description="Import conversation data into a session",
                requires_approval=True,
                risk_level="high",
                example_usage="Import conversation data",
                parameters={
                    "session_id": "Session ID to import into",
                    "data": "JSON data to import",
                    "format": "Import format (default: 'json')"
                },
                tags=["memory", "import", "restore", "data"]
            ),
            "cleanup_old_sessions": ToolConfig(
                name="cleanup_old_sessions",
                category=ToolCategory.MEMORY,
                description="Clean up conversation sessions older than specified days",
                requires_approval=True,
                risk_level="medium",
                example_usage="Clean up old conversations",
                parameters={"days_old": "Age threshold in days (default: 30)"},
                tags=["memory", "cleanup", "maintenance", "optimization"]
            ),
            "get_memory_summary": ToolConfig(
                name="get_memory_summary",
                category=ToolCategory.MEMORY,
                description="Get overall memory usage summary across all sessions",
                requires_approval=False,
                risk_level="low",
                example_usage="Show memory usage summary",
                parameters={},
                tags=["memory", "summary", "overview", "statistics"]
            ),
            "trim_session_messages": ToolConfig(
                name="trim_session_messages",
                category=ToolCategory.MEMORY,
                description="Trim a session to keep only the most recent messages",
                requires_approval=True,
                risk_level="medium",
                example_usage="Keep only recent messages",
                parameters={
                    "session_id": "Session ID to trim",
                    "max_messages": "Maximum messages to keep (default: 100)"
                },
                tags=["memory", "trim", "optimization", "cleanup"]
            )
        }
    
    def _create_memory_info_tool(self):
        """Create basic memory info tool"""
        @tool
        def memory_info(session_id: str = "default") -> str:
            """Get basic information about conversation memory."""
            try:
                stats = self.memory_manager.get_memory_stats(session_id)
                return f"💾 Memory contains {stats.message_count} messages, {stats.total_tokens} tokens, {stats.memory_size_bytes} bytes"
            except Exception as e:
                return f"Error getting memory info: {str(e)}"
        
        return memory_info
    
    def _create_memory_stats_tool(self):
        """Create detailed memory statistics tool"""
        @tool
        def get_memory_stats(session_id: str = "default") -> str:
            """Get detailed memory statistics for a specific session."""
            try:
                stats = self.memory_manager.get_memory_stats(session_id)
                
                result = f"📊 Memory Statistics for Session '{session_id}':\n"
                result += f"• Messages: {stats.message_count:,}\n"
                result += f"• Tokens: {stats.total_tokens:,}\n"
                result += f"• Memory Size: {stats.memory_size_bytes:,} bytes"
                
                # Convert bytes to more readable format
                if stats.memory_size_bytes >= 1024 * 1024:
                    result += f" ({stats.memory_size_bytes / (1024 * 1024):.2f} MB)"
                elif stats.memory_size_bytes >= 1024:
                    result += f" ({stats.memory_size_bytes / 1024:.2f} KB)"
                result += "\n"
                
                if stats.first_message_time:
                    result += f"• First Message: {stats.first_message_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                if stats.last_message_time:
                    result += f"• Last Message: {stats.last_message_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                # Calculate session duration
                if stats.first_message_time and stats.last_message_time:
                    duration = stats.last_message_time - stats.first_message_time
                    if duration.total_seconds() > 0:
                        hours = duration.total_seconds() / 3600
                        if hours >= 24:
                            result += f"• Session Duration: {duration.days} days, {hours % 24:.1f} hours\n"
                        elif hours >= 1:
                            result += f"• Session Duration: {hours:.1f} hours\n"
                        else:
                            result += f"• Session Duration: {duration.total_seconds() / 60:.1f} minutes\n"
                
                # Average statistics
                if stats.message_count > 0:
                    avg_tokens_per_message = stats.total_tokens / stats.message_count
                    avg_bytes_per_message = stats.memory_size_bytes / stats.message_count
                    result += f"• Average tokens per message: {avg_tokens_per_message:.1f}\n"
                    result += f"• Average bytes per message: {avg_bytes_per_message:.0f}\n"
                
                return result
            except Exception as e:
                return f"Error getting memory stats: {str(e)}"
        
        return get_memory_stats
    
    def _create_all_sessions_tool(self):
        """Create tool to list all sessions"""
        @tool
        def get_all_sessions() -> str:
            """Get a list of all available conversation sessions."""
            try:
                sessions = self.memory_manager.get_all_sessions()
                
                if not sessions:
                    return "📋 No conversation sessions found."
                
                result = f"📋 Available Sessions ({len(sessions)} total):\n\n"
                for i, session_id in enumerate(sessions, 1):
                    stats = self.memory_manager.get_memory_stats(session_id)
                    result += f"{i}. '{session_id}'\n"
                    result += f"   📊 {stats.message_count} messages, {stats.memory_size_bytes:,} bytes\n"
                    if stats.last_message_time:
                        result += f"   🕒 Last active: {stats.last_message_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += "\n"
                
                return result
            except Exception as e:
                return f"Error getting sessions: {str(e)}"
        
        return get_all_sessions
    
    def _create_clear_session_tool(self):
        """Create tool to clear a session"""
        @tool
        def clear_session(session_id: str) -> str:
            """Clear all conversation history for a specific session."""
            def _clear_session():
                try:
                    success = self.memory_manager.clear_session(session_id)
                    if success:
                        return f"✅ Successfully cleared session '{session_id}'"
                    else:
                        return f"❌ Failed to clear session '{session_id}'"
                except Exception as e:
                    return f"Error clearing session: {str(e)}"
            
            return self.request_approval(f"Clear session: {session_id}", _clear_session)
        
        return clear_session
    
    def _create_export_session_tool(self):
        """Create tool to export session data"""
        @tool
        def export_session(session_id: str, format: str = "json") -> str:
            """Export conversation data from a session in JSON format."""
            try:
                exported_data = self.memory_manager.export_session(session_id, format)
                
                # For display purposes, show a summary instead of full data
                data = json.loads(exported_data)
                stats = data.get("stats", {})
                message_count = stats.get("message_count", 0)
                
                result = f"📤 Exported session '{session_id}':\n"
                result += f"• Format: {format.upper()}\n"
                result += f"• Messages: {message_count:,}\n"
                result += f"• Data size: {len(exported_data):,} characters\n"
                result += f"• Export timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                # Show first part of the data for verification
                result += "💾 Export data preview (first 300 chars):\n"
                preview = exported_data[:300]
                result += f"```json\n{preview}{'...' if len(exported_data) > 300 else ''}\n```"
                
                return result
            except Exception as e:
                return f"Error exporting session: {str(e)}"
        
        return export_session
    
    def _create_import_session_tool(self):
        """Create tool to import session data"""
        @tool
        def import_session(session_id: str, data: str, format: str = "json") -> str:
            """Import conversation data into a session from JSON format."""
            def _import_session():
                try:
                    success = self.memory_manager.import_session(session_id, data, format)
                    if success:
                        stats = self.memory_manager.get_memory_stats(session_id)
                        return f"✅ Successfully imported data into session '{session_id}'\n• Messages imported: {stats.message_count:,}\n• Memory size: {stats.memory_size_bytes:,} bytes"
                    else:
                        return f"❌ Failed to import data into session '{session_id}'"
                except Exception as e:
                    return f"Error importing session: {str(e)}"
            
            return self.request_approval(f"Import data into session: {session_id}", _import_session)
        
        return import_session
    
    def _create_cleanup_sessions_tool(self):
        """Create tool to cleanup old sessions"""
        @tool
        def cleanup_old_sessions(days_old: int = 30) -> str:
            """Clean up conversation sessions older than specified number of days."""
            def _cleanup():
                try:
                    cleaned_count = self.memory_manager.cleanup_old_sessions(days_old)
                    if cleaned_count > 0:
                        return f"🧹 Cleaned up {cleaned_count} sessions older than {days_old} days"
                    else:
                        return f"✨ No sessions found older than {days_old} days - all sessions are recent!"
                except Exception as e:
                    return f"Error cleaning up sessions: {str(e)}"
            
            return self.request_approval(f"Cleanup sessions older than {days_old} days", _cleanup)
        
        return cleanup_old_sessions
    
    def _create_memory_summary_tool(self):
        """Create tool for memory summary"""
        @tool
        def get_memory_summary() -> str:
            """Get an overall summary of memory usage across all sessions."""
            try:
                summary = self.memory_manager.get_memory_summary()
                
                result = "📈 Overall Memory Summary:\n\n"
                result += f"🗂️ Sessions: {summary['total_sessions']:,}\n"
                result += f"💬 Total Messages: {summary['total_messages']:,}\n"
                
                # Format memory size
                total_bytes = summary['total_memory_bytes']
                if total_bytes >= 1024 * 1024:
                    memory_str = f"{total_bytes:,} bytes ({total_bytes / (1024 * 1024):.2f} MB)"
                elif total_bytes >= 1024:
                    memory_str = f"{total_bytes:,} bytes ({total_bytes / 1024:.2f} KB)"
                else:
                    memory_str = f"{total_bytes:,} bytes"
                result += f"💾 Total Memory: {memory_str}\n"
                
                result += f"📊 Average Messages/Session: {summary['average_messages_per_session']:.1f}\n\n"
                
                if summary['total_sessions'] > 0:
                    result += "📋 Session Details:\n"
                    for session_data in summary['sessions'][:10]:  # Show first 10 sessions
                        result += f"• '{session_data['session_id']}': {session_data['message_count']:,} messages"
                        if session_data.get('memory_size_bytes'):
                            size_kb = session_data['memory_size_bytes'] / 1024
                            result += f" ({size_kb:.1f} KB)"
                        result += "\n"
                    
                    if summary['total_sessions'] > 10:
                        result += f"... and {summary['total_sessions'] - 10} more sessions\n"
                
                return result
            except Exception as e:
                return f"Error getting memory summary: {str(e)}"
        
        return get_memory_summary
    
    def _create_trim_session_tool(self):
        """Create tool to trim session messages"""
        @tool
        def trim_session_messages(session_id: str, max_messages: int = 100) -> str:
            """Trim a session to keep only the most recent messages."""
            def _trim_session():
                try:
                    removed_count = self.memory_manager.trim_session_messages(session_id, max_messages)
                    if removed_count > 0:
                        return f"✂️ Trimmed {removed_count} old messages from session '{session_id}', keeping {max_messages} most recent messages"
                    else:
                        current_stats = self.memory_manager.get_memory_stats(session_id)
                        return f"ℹ️ Session '{session_id}' already has {current_stats.message_count} messages or fewer - no trimming needed"
                except Exception as e:
                    return f"Error trimming session: {str(e)}"
            
            return self.request_approval(f"Trim session '{session_id}' to {max_messages} messages", _trim_session)
        
        return trim_session_messages 