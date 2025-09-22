from mcp.server.fastmcp import FastMCP
import requests
import subprocess
import os
import platform
from .vector_db import VectorDB

# Try to load dotenv, but don't fail if it's not available
try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

# Create an MCP server
mcp = FastMCP("Search Service")

@mcp.tool(description="Perform a Google search and return relevant results.")
def google_search(query: str) -> str:
    """
    Perform a Google search and return relevant results with titles, snippets, and URLs.
    
    Args:
        query: The search query string to look for
        
    Returns:
        A formatted string containing Google search results
    """
    try:
        # Google Custom Search API configuration
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        
        if not api_key or not search_engine_id:
            return "Google API keys not configured. Please set GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID in your .env file."
        
        # Google Custom Search API endpoint
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": search_engine_id,
            "q": query,
            "num": 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "items" not in data:
            return f"No Google search results found for '{query}'"
        
        results = []
        for item in data["items"]:
            title = item.get("title", "No title")
            snippet = item.get("snippet", "No description")
            link = item.get("link", "No URL")
            
            # Clean up snippet text - remove extra whitespace and special characters
            snippet = snippet.replace('\xa0', ' ').replace('\n', ' ').strip()
            # Limit snippet length for readability
            if len(snippet) > 200:
                snippet = snippet[:200] + "..."
            
            results.append({
                "title": title,
                "snippet": snippet,
                "url": link
            })
        
        # Create a well-structured result format
        result_text = f"🔍 Google Search Results for '{query}'\n"
        result_text += f"Found {len(results)} results:\n\n"
        
        for i, result in enumerate(results, 1):
            result_text += f"📄 Result {i}:\n"
            result_text += f"Title: {result['title']}\n"
            result_text += f"Summary: {result['snippet']}\n"
            result_text += f"Link: {result['url']}\n"
            result_text += "-" * 50 + "\n\n"
        
        return result_text
        
    except Exception as e:
        return f"❌ Error performing Google search: {str(e)}"

@mcp.tool(description="Execute a command line interface (CLI) command and return its output.")
def execute_cli_command(command: str, working_directory: str = "", timeout: int = 30) -> str:
    """
    Execute a CLI command and return its output.
    
    Args:
        command: The command to execute (e.g., "dir", "ls -la", "python --version")
        working_directory: Optional directory to run the command in (defaults to current directory)
        timeout: Maximum time in seconds to wait for command completion (default: 30)
        
    Returns:
        A formatted string containing the command output, error messages, and execution status
    """
    try:
        # Security: Basic command validation
        dangerous_commands = [
            'rm -rf', 'del /f /s /q', 'format', 'fdisk', 'mkfs',
            'shutdown', 'reboot', 'halt', 'poweroff', 'sudo rm',
            'dd if=', 'chmod 777', 'chown -R'
        ]
        
        command_lower = command.lower()
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                return f"❌ Security: Command '{command}' contains potentially dangerous operations and cannot be executed."
        
        # Determine shell based on OS
        is_windows = platform.system() == "Windows"
        
        # Set working directory
        cwd = working_directory if working_directory != "" and os.path.exists(working_directory) else os.getcwd()
        
        # Execute command
        if is_windows:
            # On Windows, use cmd.exe
            result = subprocess.run(
                ["cmd", "/c", command],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False
            )
        else:
            # On Unix-like systems, use bash
            result = subprocess.run(
                ["bash", "-c", command],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=False
            )
        
        # Format the output
        output_text = f"💻 CLI Command Execution\n"
        output_text += f"Command: {command}\n"
        output_text += f"Working Directory: {cwd}\n"
        output_text += f"Exit Code: {result.returncode}\n"
        output_text += "-" * 50 + "\n\n"
        
        if result.stdout:
            output_text += f"📄 Output:\n{result.stdout}\n"
        
        if result.stderr:
            output_text += f"⚠️ Error Output:\n{result.stderr}\n"
        
        if result.returncode == 0:
            output_text += "✅ Command executed successfully"
        else:
            output_text += f"❌ Command failed with exit code {result.returncode}"
        
        return output_text
        
    except subprocess.TimeoutExpired:
        return f"⏰ Command '{command}' timed out after {timeout} seconds"
    except FileNotFoundError:
        return f"❌ Command not found: '{command}'. Make sure the command exists and is in your PATH."
    except PermissionError:
        return f"❌ Permission denied: Cannot execute '{command}'. Check your permissions."
    except Exception as e:
        return f"❌ Error executing command '{command}': {str(e)}"

@mcp.tool(description="List files and directories in a specified path.")
def list_directory(path: str = ".", show_hidden: bool = False) -> str:
    """
    List files and directories in the specified path.
    
    Args:
        path: The directory path to list (default: current directory)
        show_hidden: Whether to show hidden files/directories (default: False)
        
    Returns:
        A formatted string containing the directory listing
    """
    try:
        if not os.path.exists(path):
            return f"❌ Path does not exist: {path}"
        
        if not os.path.isdir(path):
            return f"❌ Path is not a directory: {path}"
        
        # Get absolute path for clarity
        abs_path = os.path.abspath(path)
        
        # List directory contents
        items = os.listdir(abs_path)
        
        # Filter hidden files if requested
        if not show_hidden:
            items = [item for item in items if not item.startswith('.')]
        
        # Sort items (directories first, then files)
        directories = []
        files = []
        
        for item in sorted(items):
            item_path = os.path.join(abs_path, item)
            if os.path.isdir(item_path):
                directories.append(f"📁 {item}/")
            else:
                file_size = os.path.getsize(item_path)
                size_str = f"({file_size} bytes)"
                files.append(f"📄 {item} {size_str}")
        
        # Format output
        output_text = f"📂 Directory Listing: {abs_path}\n"
        output_text += "-" * 50 + "\n"
        
        if directories:
            output_text += "Directories:\n"
            for dir_item in directories:
                output_text += f"  {dir_item}\n"
            output_text += "\n"
        
        if files:
            output_text += "Files:\n"
            for file_item in files:
                output_text += f"  {file_item}\n"
        
        if not directories and not files:
            output_text += "Directory is empty\n"
        
        output_text += f"\nTotal: {len(directories)} directories, {len(files)} files"
        
        return output_text
        
    except PermissionError:
        return f"❌ Permission denied: Cannot access directory '{path}'"
    except Exception as e:
        return f"❌ Error listing directory '{path}': {str(e)}"

@mcp.tool(description="Manage user memory using the vector database.")
def get_memory(user_id: str, action: str, text: str) -> str:
    """
    Get memory of the user using vector database.
    
    Args:
        user_id: The unique identifier for the user
        action: "save" to store memory, "load" to retrieve memory.
        text: The memory text to save (required if action="save") or query to search for memory.
        
    Returns:
        A string representing the user's memory
    """
    if action not in ["save", "load"]:
        return "❌ Invalid action. Use 'save' or 'load'."
    
    db = VectorDB(persist_dir=f"./user_memory_db/{user_id}")

    if action == "save":
        db.add([text])
        return f"Memory for user {user_id} has been saved."
    else:  # action == "load"
        memory = db.query(text=text)
        return f"Memory for user {user_id}: {memory["documents"]}"

# Start the MCP server
if __name__ == "__main__":
    mcp.run()