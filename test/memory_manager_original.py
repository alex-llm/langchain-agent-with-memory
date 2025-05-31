"""
Memory Manager Module - Backward Compatibility Wrapper

This module provides backward compatibility for the memory management system
that has been migrated to the memory/ directory.

All functionality is now available through:
- memory.MemoryManager
- memory.create_memory_manager
- memory.get_default_memory_manager

This file maintains backward compatibility with existing code.
"""

# Import everything from the new modular memory system
from memory import *
from memory.manager import *

# Re-export for backward compatibility
__all__ = [
    # Core memory management
    "MemoryManager",
    "MemoryStats", 
    "BaseMemoryStore",
    "InMemoryStore",
    "FileBasedMemoryStore",
    "create_memory_manager",
    "get_default_memory_manager",
    "SimpleChatMessageHistory"
]

# Add deprecation notice for future reference
import warnings

def _deprecation_warning():
    """Issue a deprecation warning for direct import"""
    warnings.warn(
        "Importing from memory_manager.py is deprecated. "
        "Please use 'from memory import MemoryManager' instead.",
        DeprecationWarning,
        stacklevel=3
    )

# Optionally show deprecation warning (commented out to avoid noise during migration)
# _deprecation_warning() 