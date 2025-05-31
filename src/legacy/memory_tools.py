"""
Memory Tools Module - Backward Compatibility Wrapper

This module provides backward compatibility for memory tools that have been
migrated to the memory/ directory.

All functionality is now available through:
- memory.MemoryTools
- memory.create_memory_tools
- memory.create_basic_memory_info_tool

This file maintains backward compatibility with existing code.
"""

# Import everything from the new modular memory system
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from memory import *
from memory.tools import *

# Re-export for backward compatibility
__all__ = [
    "MemoryTools",
    "create_memory_tools",
    "create_basic_memory_info_tool"
]

# Add deprecation notice for future reference
import warnings

def _deprecation_warning():
    """Issue a deprecation warning for direct import"""
    warnings.warn(
        "Importing from memory_tools.py is deprecated. "
        "Please use 'from memory import MemoryTools' instead.",
        DeprecationWarning,
        stacklevel=3
    )

# Optionally show deprecation warning (commented out to avoid noise during migration)
# _deprecation_warning() 