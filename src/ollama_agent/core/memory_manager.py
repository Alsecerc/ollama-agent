#!/usr/bin/env python3
"""
Memory Management Utility
Provides easy access to memory operations without creating a full AI model instance
"""

from ollama_agent.core.model_loader import ModelConfigLoader
from pathlib import Path
import json

class MemoryManager:
    """
    Memory management system for the Ollama Agent.
    Handles loading, saving, and managing conversation history.
    """
    
    def __init__(self, model_loader=None):
        """Initialize the memory manager with default paths."""
        # Set up the data directory path for memory storage  
        self.script_dir = Path(__file__).parent.parent.parent  # Go up to project root from src/ollama_agent/core/
        self.data_dir = self.script_dir / "data"
        self.memory_file = self.data_dir / "memory.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Use provided model loader or create new one
        self.loader = model_loader if model_loader else ModelConfigLoader()
    
    def clear_memory(self, keep_system_prompt=True) -> bool:
        """
        Clear memory, optionally keeping the system prompt
        
        Args:
            keep_system_prompt: If True, keeps the system message and token count
        """
        try:
            # Load existing memory
            with open(self.memory_file, 'r') as f:
                history = json.load(f)
            
            if keep_system_prompt:
                # Keep only system and token_count messages
                new_history = []
                for message in history:
                    if message.get('role') in ['system', 'token_count']:
                        if message.get('role') == "token_count":
                            message['content'] = "0"
                        new_history.append(message)
                history = new_history
            else:
                # Clear everything
                history = []
            
            # Save cleared memory
            with open(self.memory_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            print(f"✅ Memory cleared successfully! {'(System prompt preserved)' if keep_system_prompt else '(Complete clear)'}")
            return True
            
        except FileNotFoundError:
            print("📝 No memory file found - creating empty memory")
            with open(self.memory_file, 'w') as f:
                json.dump([], f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error clearing memory: {e}")
            return False
    
    def view_memory(self) -> None:
        """View current memory contents"""
        try:
            with open(self.memory_file, 'r') as f:
                history = json.load(f)
            
            if not history:
                print("📝 Memory is empty")
                return
            
            print(f"📚 Memory contains {len(history)} messages:")
            for i, message in enumerate(history, 1):
                role = message.get('role', 'unknown')
                content = message.get('content', '')[:100]  # First 100 chars
                if len(message.get('content', '')) > 100:
                    content += "..."
                print(f"  {i}. {role}: {content}")
                
        except FileNotFoundError:
            print("📝 No memory file found")
        except Exception as e:
            print(f"❌ Error reading memory: {e}")
    
    def get_memory_stats(self) -> dict:
        """Get memory statistics"""
        try:
            with open(self.memory_file, 'r') as f:
                history = json.load(f)
            
            stats = {
                'total_messages': len(history),
                'user_messages': len([m for m in history if m.get('role') == 'user']),
                'assistant_messages': len([m for m in history if m.get('role') == 'assistant']),
                'system_messages': len([m for m in history if m.get('role') == 'system'])
            }
            
            print("📊 Memory Statistics:")
            for key, value in stats.items():
                print(f"  {key.replace('_', ' ').title()}: {value}")
            
            return stats
            
        except FileNotFoundError:
            print("📝 No memory file found")
            return {}
        except Exception as e:
            print(f"❌ Error reading memory: {e}")
            return {}