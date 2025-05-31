"""
Memory Module for LangChain Agent

A comprehensive memory management system that provides:
- Multiple memory store types (in-memory, file-based)
- Session-based memory isolation
- Memory persistence and serialization
- Memory statistics and analysis
- Memory cleanup and optimization
- Memory-related tools for LangChain agents

Usage:
    from memory import MemoryManager, create_memory_manager, MemoryTools
    
    # Create a memory manager
    memory_manager = create_memory_manager(store_type="file")
    
    # Create memory tools
    memory_tools = MemoryTools(memory_manager)
    tools = memory_tools.get_tools()
"""

from .manager import (
    MemoryManager,
    MemoryStats,
    BaseMemoryStore,
    InMemoryStore,
    FileBasedMemoryStore,
    create_memory_manager,
    get_default_memory_manager
)

from .tools import (
    MemoryTools,
    create_memory_tools,
    create_basic_memory_info_tool
)

__version__ = "1.0.0"
__all__ = [
    # Core memory management
    "MemoryManager",
    "MemoryStats", 
    "BaseMemoryStore",
    "InMemoryStore",
    "FileBasedMemoryStore",
    "create_memory_manager",
    "get_default_memory_manager",
    
    # Memory tools
    "MemoryTools",
    "create_memory_tools", 
    "create_basic_memory_info_tool"
]

# Backward compatibility imports
# These allow existing code to continue working without changes
def create_memory_manager_compat(store_type: str = "memory", **kwargs):
    """Backward compatibility wrapper for create_memory_manager"""
    return create_memory_manager(store_type, **kwargs)

def get_default_memory_manager_compat():
    """Backward compatibility wrapper for get_default_memory_manager"""
    return get_default_memory_manager() 