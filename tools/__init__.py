"""
Tools Module for LangChain Agent

A modular tool system that provides organized, maintainable, and extensible tools
for LangChain agents. This module supports:

- Basic utility tools (calculator, time, text analysis)
- Advanced tools (web search, file operations, weather)
- Memory management tools
- MCP (Model Context Protocol) tools
- User approval system for sensitive operations
- Tool categorization and configuration management

Usage:
    from tools import ToolRegistry, get_available_tools
    
    # Get all available tools
    tools = get_available_tools()
    
    # Get tools by category
    basic_tools = get_available_tools(categories=['utility', 'information'])
    
    # Create tool registry with specific configuration
    registry = ToolRegistry(
        enable_user_approval=True,
        enabled_categories=['utility', 'information'],
        memory_manager=memory_manager
    )
    tools = registry.get_tools()
"""

from .registry import ToolRegistry, ToolConfig, ToolCategory
from .basic_tools import BasicToolsModule
from .advanced_tools import AdvancedToolsModule
from .memory_tools_module import MemoryToolsModule
from .mcp_tools import MCPToolsModule

__version__ = "1.0.0"
__all__ = [
    "ToolRegistry",
    "ToolConfig", 
    "ToolCategory",
    "BasicToolsModule",
    "AdvancedToolsModule", 
    "MemoryToolsModule",
    "MCPToolsModule",
    "get_available_tools",
    "get_tool_info",
    "create_tool_registry"
]


def get_available_tools(categories=None, enabled_tools=None, **kwargs):
    """
    Get available tools with optional filtering
    
    Args:
        categories: List of tool categories to include
        enabled_tools: List of specific tool names to include
        **kwargs: Additional configuration for tool registry
    
    Returns:
        List of LangChain tool instances
    """
    registry = ToolRegistry(**kwargs)
    return registry.get_tools(categories=categories, enabled_tools=enabled_tools)


def get_tool_info():
    """
    Get information about all available tools
    
    Returns:
        Dictionary containing tool information organized by category
    """
    registry = ToolRegistry()
    return registry.get_tool_info()


def create_tool_registry(**kwargs):
    """
    Create a new tool registry with custom configuration
    
    Args:
        **kwargs: Configuration options for the tool registry
    
    Returns:
        ToolRegistry instance
    """
    return ToolRegistry(**kwargs) 