import os
from pathlib import Path
from ollama import Client
from ollama._types import ResponseError  # Import the error type
import subprocess
import psutil
import json

class AIModel:
    """
    Base class for AI models.
    This class should be extended by specific AI model implementations.
    """

    def __init__(self, model_name: str, temperature: float = 0.1, max_tokens: int = 1000, system_instruction: str = "", available_functions: list = [], max_history_length: int = 15):
        """
        
        Initialize the AI model with the given parameters.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = Client("http://localhost:11434")
        self.system_instruction = system_instruction
        self.avaliable_functions = available_functions
        self.history = []
        self.max_history_length = max_history_length
        
        # Set up the data directory path for memory storage
        self.script_dir = Path(__file__).parent.parent.parent.parent  # Go up one level from agent/ to project root
        self.data_dir = self.script_dir / "data"
        self.memory_file = self.data_dir / "memory.json"
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
        # Load existing memory if it exists
        self.load_memory()

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response based on the provided prompt without memory.
        """
        response = self.client.generate(
            model=self.model_name,
            prompt=prompt,
            system=self.system_instruction,
        )
        # Fix: Use 'response' key instead of 'message'['content']
        return response['response']
    
    def chat(self, message: str, isCallTool: bool = False) -> str:
        """
        Generate a chat response based on the provided messages and available functions.
        """
        if not message:
            raise ValueError("Messages string cannot be empty.")

        if isCallTool:
            self.history[-1] = {'role': 'assistant', 'content': message}

        # Load latest memory state
        self.load_memory()
        
        # Check if system role exists in history, if not add it
        has_system_role = any(msg.get('role') == 'system' for msg in self.history)
        if not has_system_role:
            self.history.insert(0, {'role': 'system', 'content': self.system_instruction})
        
        # Append user message to history
        self.history.append({'role': 'user', 'content': message})
        
        # Use the full history for the chat
        messages = self.history.copy()

        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            tools=self.avaliable_functions,
            stream=False
        )

        try:
            # Parse the JSON string returned by model_dump_json()
            response_json_str = response.model_dump_json()
            response_data:dict = json.loads(response_json_str)
            
            # Access response data safely
            self.prompt_eval_count = response_data.get('prompt_eval_count', 0)
            assistant_message = response_data.get('message', {}).get('content', '')
            self.no_of_tokens = response_data.get('eval_count', 0)
            self.eval_duration = response_data.get('eval_duration', 0)
            
            # Update history safely
            if len(self.history) > 1:
                self.history[1]['content'] = str(self.no_of_tokens)
            
            # Append assistant response to history
            self.history.append({
                'role': 'assistant',
                'content': assistant_message
            })
            
            # Check if history exceeds max length and truncate if needed
            if self.size_of_memory() > self.max_history_length:
                self.history = [self.history[0]] + self.history[-(self.max_history_length-1):]
            
            # Save updated history to memory
            with open(self.memory_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            return assistant_message
        except Exception as e:
            print(f"Error parsing response: {e}")
            # Use the correct attribute for response content
            print(f"Response message: {response.message.content if hasattr(response, 'message') else 'No message content'}")   
            return "Error: Failed to get response from model"

    @staticmethod
    def function_call_avaliablity(model) -> bool:
        """
        This function checks if the model supports function calling.
        """
        client = Client("http://localhost:11434")

        try:
            client.chat(
                model=model,
                messages=[{'role': 'user', 'content': 'What is the weather in New York?'}], 
                tools=[{
                'type': 'function',
                'function': {
                    'name': 'get_current_weather',
                    'description': 'Get current weather for a city',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'city': {'type': 'string', 'description': 'Name of city'}
                        },
                        'required': ['city']
                    }
                }
            }])
            return True
        except ResponseError:
            return False
    
    def kill_ollama_processes(self) -> None:
        """Terminate all running ollama.exe processes"""
        try:
            if not self.is_ollama_running():
                print("✅ No running ollama.exe processes found.")
                return
            # Use taskkill to terminate all instances of ollama.exe
            print("🛑 Terminating all running ollama.exe processes...")
            # /F = force, /IM = image name
            subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ All ollama.exe processes have been terminated.")
        except subprocess.CalledProcessError as e:
            print("⚠️ No ollama.exe processes were running or failed to terminate.")
            print(e)

    def is_ollama_running(self) -> bool:
        """Check if any ollama.exe process is running"""
        
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and proc.info['name'].lower() == 'ollama.exe':
                return True
        return False
    
    @staticmethod
    def list_ollama_models() -> None:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("⚠️ Failed to list models.")
            print(result.stderr)

    def load_memory(self) -> bool:
        try:
            with open(self.memory_file, 'r') as f:
                self.history = json.load(f)
                if self.size_of_memory() > self.max_history_length:
                    self.history = self.history[-self.max_history_length:]
                    with open(self.memory_file, 'w') as f:
                        json.dump(self.history, f, indent=2)
            return True
        except FileNotFoundError:
            # Create new empty memory file if it doesn't exist
            print(f"Memory file not found. Creating new memory file at {self.memory_file}")
            self.history = []
            with open(self.memory_file, 'w') as f:
                json.dump(self.history, f, indent=2)
            return True
        except Exception as e:
            print(f"Error loading memory: {e}")
            return False

    def size_of_memory(self) -> int:
        return len(self.history)

    def clear_memory(self) -> None:
        message: dict
        self.history_new = []
        for message in self.history:
            if message['role'] == 'system' or message['role'] == 'token_count':
                if message.get('role') == "token_count":
                    message['content'] = "0"
                self.history_new.append(message)
        self.history = self.history_new
        with open(self.memory_file, 'w') as f:
            json.dump(self.history, f, indent=2)