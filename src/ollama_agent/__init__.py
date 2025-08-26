"""
Ollama Agent - Intelligent AI-powered command-line assistant with MCP integration.

This package provides a sophisticated AI agent system that leverages the Model Context Protocol (MCP) 
and Ollama to provide intelligent responses and tool execution capabilities through a global 
command-line interface.
"""

__version__ = "0.1.0"
__author__ = "Chen"
__email__ = "your.email@example.com"
__description__ = "Intelligent Agent CLI - AI-powered command-line assistant with MCP integration"

# Make key classes available at package level
from .core.agent import IntelligentAgent
from .core.model_loader import ModelConfigLoader
from .core.memory_manager import MemoryManager

__all__ = [
    "IntelligentAgent",
    "ModelConfigLoader", 
    "MemoryManager",
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]