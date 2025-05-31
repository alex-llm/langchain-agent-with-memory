"""
Memory Tools Module - Root Compatibility Wrapper

This module provides backward compatibility for memory tools.
The actual compatibility wrapper is now located in src/legacy/memory_tools.py

Usage:
    from memory_tools import MemoryTools, create_memory_tools

For new projects, please use:
    from memory import MemoryTools, create_memory_tools
"""

# Import from the legacy compatibility wrapper
import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import from legacy wrapper
from legacy.memory_tools import *

# Re-export everything for compatibility
__all__ = [
    "MemoryTools",
    "create_memory_tools",
    "create_basic_memory_info_tool"
] 