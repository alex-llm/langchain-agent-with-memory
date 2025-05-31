"""
Tool Registry System

Central registry for managing all tools, their configurations, categories,
and access control. This system provides:

- Tool discovery and registration
- Category-based organization  
- Permission and approval management
- Configuration management
- Tool metadata and documentation
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Tool categories for organization and filtering"""
    UTILITY = "utility"           # Basic utility tools (calculator, text analysis)
    INFORMATION = "information"   # Information retrieval (time, weather, facts)
    PRODUCTIVITY = "productivity" # Productivity tools (notes, file operations)
    COMMUNICATION = "communication" # Communication tools (web search, email)
    MEMORY = "memory"            # Memory management tools
    SYSTEM = "system"            # System administration tools
    ENTERTAINMENT = "entertainment" # Entertainment and fun tools
    MCP = "mcp"                  # Model Context Protocol tools
    CUSTOM = "custom"            # Custom user-defined tools


@dataclass
class ToolConfig:
    """Configuration for a single tool"""
    name: str
    category: ToolCategory
    description: str
    requires_approval: bool = False
    risk_level: str = "low"  # low, medium, high
    enabled: bool = True
    example_usage: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "requires_approval": self.requires_approval,
            "risk_level": self.risk_level,
            "enabled": self.enabled,
            "example_usage": self.example_usage,
            "parameters": self.parameters,
            "tags": self.tags
        }


class BaseToolModule:
    """Base class for tool modules"""
    
    def __init__(self, memory_manager=None, enable_user_approval=False):
        self.memory_manager = memory_manager
        self.enable_user_approval = enable_user_approval
        self._approval_handler = None
    
    def set_approval_handler(self, handler: Callable):
        """Set the approval handler function"""
        self._approval_handler = handler
    
    def request_approval(self, description: str, action: Callable) -> Any:
        """Request approval for an action"""
        if self.enable_user_approval and self._approval_handler:
            return self._approval_handler(description, action)
        else:
            return action()
    
    def get_tools(self) -> List:
        """Get all tools from this module (must be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement get_tools method")
    
    def get_tool_configs(self) -> Dict[str, ToolConfig]:
        """Get tool configurations (must be implemented by subclasses)"""
        raise NotImplementedError("Subclasses must implement get_tool_configs method")


class ToolRegistry:
    """Central registry for managing all tools"""
    
    def __init__(self, 
                 memory_manager=None,
                 enable_user_approval: bool = False,
                 enabled_categories: Optional[List[Union[str, ToolCategory]]] = None,
                 enabled_tools: Optional[List[str]] = None,
                 approval_handler: Optional[Callable] = None,
                 mcp_servers: Optional[List[Dict]] = None):
        """
        Initialize tool registry
        
        Args:
            memory_manager: Memory manager instance for memory tools
            enable_user_approval: Whether to enable user approval for sensitive operations
            enabled_categories: List of enabled tool categories
            enabled_tools: List of specific enabled tool names
            approval_handler: Function to handle approval requests
            mcp_servers: MCP server configurations
        """
        self.memory_manager = memory_manager
        self.enable_user_approval = enable_user_approval
        self.approval_handler = approval_handler
        self.mcp_servers = mcp_servers or []
        
        # Convert category names to enums
        if enabled_categories:
            self.enabled_categories = []
            for cat in enabled_categories:
                if isinstance(cat, str):
                    try:
                        self.enabled_categories.append(ToolCategory(cat))
                    except ValueError:
                        logger.warning(f"Invalid category: {cat}")
                else:
                    self.enabled_categories.append(cat)
        else:
            self.enabled_categories = list(ToolCategory)
        
        self.enabled_tools = enabled_tools
        self._modules = {}
        self._tool_configs = {}
        self._initialize_modules()
    
    def _initialize_modules(self):
        """Initialize all tool modules"""
        # Import here to avoid circular imports
        from .basic_tools import BasicToolsModule
        from .advanced_tools import AdvancedToolsModule
        from .memory_tools_module import MemoryToolsModule
        from .mcp_tools import MCPToolsModule
        
        # Initialize modules
        modules = [
            ("basic", BasicToolsModule),
            ("advanced", AdvancedToolsModule),
            ("memory", MemoryToolsModule),
            ("mcp", MCPToolsModule)
        ]
        
        for module_name, module_class in modules:
            try:
                # Special handling for modules that need extra parameters
                if module_name == "memory" and self.memory_manager:
                    module = module_class(
                        memory_manager=self.memory_manager,
                        enable_user_approval=self.enable_user_approval
                    )
                elif module_name == "mcp":
                    module = module_class(
                        mcp_servers=self.mcp_servers,
                        enable_user_approval=self.enable_user_approval
                    )
                else:
                    module = module_class(
                        memory_manager=self.memory_manager,
                        enable_user_approval=self.enable_user_approval
                    )
                
                # Set approval handler
                if self.approval_handler:
                    module.set_approval_handler(self.approval_handler)
                
                self._modules[module_name] = module
                
                # Load tool configurations
                configs = module.get_tool_configs()
                self._tool_configs.update(configs)
                
                logger.info(f"Initialized {module_name} tools module with {len(configs)} tools")
                
            except Exception as e:
                logger.error(f"Failed to initialize {module_name} module: {e}")
    
    def get_tools(self, 
                  categories: Optional[List[Union[str, ToolCategory]]] = None,
                  enabled_tools: Optional[List[str]] = None) -> List:
        """
        Get tools based on filtering criteria
        
        Args:
            categories: Categories to include (overrides instance setting)
            enabled_tools: Specific tools to include (overrides instance setting)
        
        Returns:
            List of LangChain tool instances
        """
        # Use provided parameters or fall back to instance settings
        filter_categories = categories or self.enabled_categories
        filter_tools = enabled_tools or self.enabled_tools
        
        # Convert category names to enums if needed
        if filter_categories:
            category_enums = []
            for cat in filter_categories:
                if isinstance(cat, str):
                    try:
                        category_enums.append(ToolCategory(cat))
                    except ValueError:
                        logger.warning(f"Invalid category: {cat}")
                else:
                    category_enums.append(cat)
            filter_categories = category_enums
        
        all_tools = []
        
        for module_name, module in self._modules.items():
            try:
                module_tools = module.get_tools()
                
                for tool in module_tools:
                    tool_name = tool.name
                    config = self._tool_configs.get(tool_name)
                    
                    if not config or not config.enabled:
                        continue
                    
                    # Filter by category
                    if filter_categories and config.category not in filter_categories:
                        continue
                    
                    # Filter by specific tool names
                    if filter_tools and tool_name not in filter_tools:
                        continue
                    
                    all_tools.append(tool)
                
            except Exception as e:
                logger.error(f"Error getting tools from {module_name}: {e}")
        
        logger.info(f"Loaded {len(all_tools)} tools based on filters")
        return all_tools
    
    def get_tool_configs(self, 
                        categories: Optional[List[Union[str, ToolCategory]]] = None) -> Dict[str, ToolConfig]:
        """Get tool configurations, optionally filtered by category"""
        if not categories:
            return self._tool_configs.copy()
        
        # Convert category names to enums if needed
        category_enums = []
        for cat in categories:
            if isinstance(cat, str):
                try:
                    category_enums.append(ToolCategory(cat))
                except ValueError:
                    continue
            else:
                category_enums.append(cat)
        
        filtered_configs = {}
        for name, config in self._tool_configs.items():
            if config.category in category_enums:
                filtered_configs[name] = config
        
        return filtered_configs
    
    def get_tool_info(self) -> Dict[str, Dict[str, Any]]:
        """Get organized tool information by category"""
        info = {}
        
        for category in ToolCategory:
            category_tools = {}
            for name, config in self._tool_configs.items():
                if config.category == category and config.enabled:
                    category_tools[name] = config.to_dict()
            
            if category_tools:
                info[category.value] = {
                    "name": category.value.title(),
                    "tools": category_tools,
                    "count": len(category_tools)
                }
        
        return info
    
    def get_tool_by_name(self, tool_name: str):
        """Get a specific tool by name"""
        for module in self._modules.values():
            try:
                tools = module.get_tools()
                for tool in tools:
                    if tool.name == tool_name:
                        return tool
            except Exception as e:
                logger.error(f"Error searching for tool {tool_name}: {e}")
        
        return None
    
    def register_custom_tool(self, tool, config: ToolConfig):
        """Register a custom tool"""
        self._tool_configs[config.name] = config
        # Custom tools would need to be handled specially
        # This is a placeholder for future custom tool support
        logger.info(f"Registered custom tool: {config.name}")
    
    def reload_modules(self):
        """Reload all tool modules (useful for development)"""
        self._modules.clear()
        self._tool_configs.clear()
        self._initialize_modules()
        logger.info("Reloaded all tool modules")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        stats = {
            "total_tools": len(self._tool_configs),
            "enabled_tools": sum(1 for config in self._tool_configs.values() if config.enabled),
            "modules_loaded": len(self._modules),
            "categories": {}
        }
        
        for category in ToolCategory:
            count = sum(1 for config in self._tool_configs.values() 
                       if config.category == category and config.enabled)
            if count > 0:
                stats["categories"][category.value] = count
        
        return stats 