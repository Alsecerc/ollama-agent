#!/usr/bin/env python3
"""
Model Configuration Loader
Utility for loading and managing model configurations from model.json
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

class ModelConfigLoader:
    """Load and manage model configurations from model.json"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the model config loader
        
        Args:
            config_path: Path to model.json file. If None, uses default location.
        """
        if config_path is None:
            # Updated path for new structure - look in config directory
            self.config_path = Path(__file__).parent.parent / 'config' / 'models.json'
        else:
            self.config_path = Path(config_path)
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                print(f"✅ Loaded model configuration from {self.config_path}")
                return config
        except FileNotFoundError:
            print(f"❌ Model configuration file not found: {self.config_path}")
            return self._get_fallback_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing model configuration: {e}")
            return self._get_fallback_config()
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Return fallback configuration if file loading fails"""
        return {
            'models': {
                'big': {
                    'name': 'gemma3:12b',
                    'parameters': {'temperature': 0.1, 'max_tokens': 1000}
                },
                'small': {
                    'name': 'gemma3:1b', 
                    'parameters': {'temperature': 0.1, 'max_tokens': 500}
                }
            },
            'settings': {
                'default_big_model': 'gemma3:12b',
                'default_small_model': 'gemma3:1b',
                'fallback_model': 'gemma3:1b'
            }
        }
    
    def get_model_name(self, model_type: str) -> str:
        """
        Get model name by type
        
        Args:
            model_type: 'big', 'small', 'tiny', etc.
            
        Returns:
            Model name string
        """
        try:
            return self.config['models'][model_type]['name']
        except KeyError:
            print(f"❌ Model type '{model_type}' not found in configuration")
            return self.config['settings']['fallback_model']
    
    def get_model_parameters(self, model_type: str) -> Dict[str, Any]:
        """
        Get model parameters by type
        
        Args:
            model_type: 'big', 'small', 'tiny', etc.
            
        Returns:
            Dictionary of model parameters
        """
        try:
            return self.config['models'][model_type]['parameters']
        except KeyError:
            print(f"❌ Parameters for model type '{model_type}' not found")
            return {'temperature': 0.1, 'max_tokens': 500}
    
    def get_default_models(self) -> Dict[str, str]:
        """Get default model names"""
        settings = self.config.get('settings', {})
        return {
            'big': settings.get('default_big_model', 'gemma3:12b'),
            'small': settings.get('default_small_model', 'gemma3:1b'),
            'fallback': settings.get('fallback_model', 'gemma3:1b')
        }
    
    def get_model_use_cases(self, model_type: str) -> List[str]:
        """
        Get use cases for a model type
        
        Args:
            model_type: 'big', 'small', 'tiny', etc.
            
        Returns:
            List of use case strings
        """
        try:
            return self.config['models'][model_type].get('use_cases', [])
        except KeyError:
            print(f"❌ Use cases for model type '{model_type}' not found")
            return []
    
    def get_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Get all model configurations"""
        return self.config.get('models', {})
    
    def get_settings(self) -> Dict[str, Any]:
        """Get all settings"""
        return self.config.get('settings', {})
    
    def print_summary(self) -> None:
        """Print a summary of loaded model configuration"""
        print("\n📋 Model Configuration Summary:")
        print("=" * 50)
        
        # Models
        models = self.get_all_models()
        for model_type, model_info in models.items():
            name = model_info.get('name', 'Unknown')
            description = model_info.get('description', 'No description')
            params = model_info.get('parameters', {})
            
            print(f"\n🤖 {model_type.upper()} Model:")
            print(f"   Name: {name}")
            print(f"   Description: {description}")
            print(f"   Temperature: {params.get('temperature', 'N/A')}")
            print(f"   Max Tokens: {params.get('max_tokens', 'N/A')}")
            print(f"   Timeout: {params.get('timeout', 'N/A')}s")
        
        # Settings
        settings = self.get_settings()
        print(f"\n⚙️ Settings:")
        for key, value in settings.items():
            print(f"   {key}: {value}")
