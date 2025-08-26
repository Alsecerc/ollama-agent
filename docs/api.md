# API Documentation

## Core Classes

### IntelligentAgent
Main agent class that handles user queries and tool selection.

**Methods:**
- `handle_user_query(user_query: str, mcp_session) -> str`
  - Process user queries and return intelligent responses
  - Parameters:
    - `user_query`: The user's question or command
    - `mcp_session`: Active MCP session for tool execution
  - Returns: AI-generated response string

### AIModel
Base class for AI model interactions with Ollama.

**Methods:**
- `chat(message: str) -> str`
  - Chat with the AI model using conversation history
- `generate_response(prompt: str) -> str`
  - Generate a single response without memory
- `load_memory() -> bool`
  - Load conversation history from storage
- `clear_memory() -> None`
  - Clear conversation history

### ModelConfigLoader
Configuration management for AI models.

**Methods:**
- `get_model_name(model_type: str) -> str`
  - Get model name by type (tiny, small, big)
- `get_model_parameters(model_type: str) -> Dict[str, Any]`
  - Get model parameters (temperature, max_tokens, etc.)
- `print_summary() -> None`
  - Display configuration summary

### MemoryManager
Manages persistent conversation memory.

**Methods:**
- `clear_memory(keep_system_prompt: bool = True) -> None`
  - Clear conversation history
- `view_memory() -> None`
  - Display current memory contents
- `get_memory_stats() -> None`
  - Show memory usage statistics

## MCP Tools

### google_search
Search the web for current information.

**Parameters:**
- `query` (string): Search query
- `num_results` (integer, optional): Number of results (default: 5)

### execute_cli_command
Execute system commands safely.

**Parameters:**
- `command` (string): Command to execute
- `working_directory` (string, optional): Directory to run command in

### list_directory
List directory contents.

**Parameters:**
- `path` (string): Directory path to list
- `show_hidden` (boolean, optional): Include hidden files (default: false)