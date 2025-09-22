"""
CLI module for Ollama Agent.

This module provides command-line interface functionality for the Ollama Agent,
including both production and development CLI entry points.
"""

# Import main CLI functions to make them available at package level
from .main import main

# Define what gets imported when someone does "from ollama_agent.cli import *"
__all__ = [
    "main",
]

# CLI module metadata
__version__ = "0.1.0"
__description__ = "Command-line interface for Ollama Agent"