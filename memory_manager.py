"""
Memory Manager Module - Root Compatibility Wrapper

This module provides backward compatibility for the memory management system.
The actual compatibility wrapper is now located in src/legacy/memory_manager.py

Usage:
    from memory_manager import MemoryManager, create_memory_manager

For new projects, please use:
    from memory import MemoryManager, create_memory_manager
"""

# Import from the legacy compatibility wrapper
import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import from legacy wrapper
from legacy.memory_manager import *

# Re-export everything for compatibility
__all__ = [
    "MemoryManager",
    "MemoryStats", 
    "BaseMemoryStore",
    "InMemoryStore",
    "FileBasedMemoryStore",
    "create_memory_manager",
    "get_default_memory_manager",
    "SimpleChatMessageHistory"
] 