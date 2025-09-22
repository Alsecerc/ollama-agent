from ollama_agent import IntelligentAgent, MemoryManager, ModelConfigLoader
import asyncio
import ollama_agent
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
import os
import sys
import argparse
import difflib
import json
import traceback
from rich.console import Console
from rich.markdown import Markdown

try:
    import dotenv
    dotenv.load_dotenv()
except ImportError:
    pass

console = Console()
isDebug:bool = IntelligentAgent.printDebug
# Create a single instance and reuse it
loader = ModelConfigLoader()
loadtinymodel = loader.get_model_name("tiny")  # Use the existing instance
manager = MemoryManager()
# loader already created above
EXIT_COMMANDS = ['quit', 'exit', 'q', 'bye', 'goodbye']
HELP_COMMANDS = ['help', '?']

ALL_COMMANDS =[
    '/memory clear', '/memory clear-all', '/memory view', '/memory stats',
    '/model summary', '/model models', '/model defaults', '/model config',
    '/quit', '/exit', '/q', '/bye', '/goodbye', '/help', '/?'
]

AVAILABLE_COMMANDS = """
Available commands:
- Enter any natural language query for the agent
- '/bye', '/exit', '/quit' - Exit the program
- '/help' - Show this help message
- '/memory clear' - Clear memory (keep system prompt)
- '/memory clear-all' - Clear all memory
- '/memory view' - View current memory
- '/memory stats' - Show memory statistics
- '/model summary' - Show model configuration summary
- '/model models' - List available models
- '/model defaults' - Show default models
- '/model config' - Show full configuration
- Ctrl+C - Force exit

Examples:
- "List files in the current directory"
- "Check the Python version"
- "Search for Python files in the project"
"""


def debug_print(debug_mode: bool = isDebug, message: str = "") -> None:
    """Print debug messages if debug mode is enabled."""
    if debug_mode:
        print(f"[DEBUG] {message}")

async def run_intelligent_agent(userquery) -> str:
    """
    Main function to run the intelligent agent that decides when to search.
    """
    
    # Get absolute path to server and use the virtual environment Python
    package_dir = os.path.dirname(ollama_agent.__file__)
    server_path = os.path.join(package_dir, "server", "mcp_server.py")
    python_path = sys.executable  # Use current Python interpreter
    params = StdioServerParameters(command=python_path, args=[server_path])
    
    try:
        async with stdio_client(params) as (r,w):
            async with ClientSession(r,w) as sess:
                await sess.initialize()
                
                tools = await sess.list_tools()

                tool_defs = []  # <-- final list in Ollama-compatible format
                tool_list_items = []

                for i, tool in enumerate(tools.tools):
                    # Build parameters schema
                    parameters = {
                        "type": "object",
                        "properties": {}
                    }

                    arg_info: dict

                    required_args = []
                    if tool.inputSchema and "properties" in tool.inputSchema:
                        for arg_name, arg_info in tool.inputSchema["properties"].items():
                            # Add each argument into properties
                            parameters["properties"][arg_name] = {
                                "type": arg_info.get("type", "string"),
                                "description": arg_info.get("description", "")
                            }
                            # If schema marks as required, include it
                            if "required" in tool.inputSchema and arg_name in tool.inputSchema["required"]:
                                required_args.append(arg_name)

                    if required_args:
                        parameters["required"] = required_args

                    # Wrap each tool as Ollama-compatible "tools" schema
                    tool_defs.append({
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": parameters
                        }
                    })

                    # Append to human-readable tool list
                    arg_list = ", ".join([
                        f"{arg_name} ({arg_info.get('type', 'unknown')})"
                        for arg_name, arg_info in (tool.inputSchema['properties'].items() if tool.inputSchema else {})
                    ])
                    tool_list_items.append(f"{i+1}. {tool.name} : {tool.description}\n   Args: {arg_list}")

                debug_print(message=f"Tool definitions: {tool_defs}")
                tool_list = "\n".join(tool_list_items)
                debug_print(message=f"Available tools:\n{tool_list}")
                intelligentAgent = IntelligentAgent(list_of_tools=tool_list, avaliable_functions=tool_defs)
                result = await intelligentAgent.handle_user_query(user_query=userquery, mcp_session=sess)
                return result
                    
    except Exception as e:
        error_msg = f"Error running intelligent agent: {e}"
        debug_print(message=error_msg)
        traceback.print_exc()
        return error_msg
    
def handle_command(main_cmd: str, args: list[str]):
    """
    Unified handler for /memory and /model commands.
    main_cmd: "memory" or "model"
    args: list of subcommands (e.g. ["view"], ["summary"])
    """
    subcommands = {
        "memory": ["clear", "clear-all", "view", "stats"],
        "model": ["summary", "models", "defaults", "config"],
    }

    if not args:
        print(f"💡 Usage: /{main_cmd} <{'|'.join(subcommands[main_cmd])}>")
        return

    raw_sub = args[0].lower()

    # Fuzzy match subcommands
    sub_cmd = difflib.get_close_matches(raw_sub, subcommands[main_cmd], n=1, cutoff=0.6)
    if not sub_cmd:
        print(f"❌ Unknown {main_cmd} command: {raw_sub}")
        print(f"💡 Available: {', '.join(subcommands[main_cmd])}")
        return

    sub_cmd = sub_cmd[0]

    if main_cmd == "memory":
        if sub_cmd == "clear":
            manager.clear_memory(keep_system_prompt=True)
        elif sub_cmd == "clear-all":
            manager.clear_memory(keep_system_prompt=False)
        elif sub_cmd == "view":
            manager.view_memory()
        elif sub_cmd == "stats":
            manager.get_memory_stats()

    elif main_cmd == "model":
        if sub_cmd == "summary":
            loader.print_summary()
        elif sub_cmd == "models":
            models = loader.get_all_models()
            print("📋 Available Models:")
            for model_type, info in models.items():
                print(f"  {model_type}: {info['name']}")
        elif sub_cmd == "defaults":
            defaults = loader.get_default_models()
            print("⚙️ Default Models:")
            for key, value in defaults.items():
                print(f"  {key}: {value}")
        elif sub_cmd == "config":
            print("📄 Full Model Configuration:")
            print(json.dumps(loader.config, indent=2))

COMMANDS={
    "memory": lambda args: handle_command("memory", args),
    "model":  lambda args: handle_command("model", args),
}

def dispatch_command(query: str) -> bool:
    """
    Handle slash commands. Returns True if handled, False if not a command.
    """
    if not query.startswith("/"):
        return False

    parts = query[1:].split()
    command = parts[0].lower() if parts else ""

    # Exit commands
    if command in EXIT_COMMANDS:
        print("👋 Goodbye!")
        sys.exit(0)

    # Help commands
    if command in HELP_COMMANDS:
        print(AVAILABLE_COMMANDS)
        return True

    # Memory / Model
    if command in COMMANDS:
        COMMANDS[command](parts[1:])
        return True

    # Fuzzy match full command
    suggestion = difflib.get_close_matches(query, ALL_COMMANDS, n=1, cutoff=0.6)
    print(f"❌ Unknown command: {query}")
    print(f"💡 Did you mean: {suggestion[0] if suggestion else 'No similar command found'}")
    return True

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Intelligent Agent CLI - Run queries through your MCP agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        python main.py "List files in current directory"
        python main.py -i  # Interactive mode
        python main.py --query "Check Python version"
        python main.py --memory clear  # Clear memory
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='Query to send to the agent'
    )
    
    parser.add_argument(
        '-q', '--query',
        dest='query_arg',
        help='Query to send to the agent (alternative to positional argument)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '-m', '--memory',
        choices=['clear', 'clear-all', 'view', 'stats'],
        help='Memory management commands: clear (keep system), clear-all (remove all), view, stats'
    )
    
    parser.add_argument(
        '--model',
        choices=['summary', 'models', 'defaults', 'config'],
        help='Model configuration commands: summary (show all), models (list names), defaults (show defaults), config (show full config)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Intelligent Agent CLI 1.0.0'
    )
    
    return parser.parse_args()

async def interactive_mode() -> None:
    """Run the agent in interactive mode."""
    print("Intelligent Agent CLI - Interactive Mode")
    print("Type '/bye', '/exit', '/quit' to exit")
    print("Type '/help' for usage information")
    print("Type '/memory <command>' for memory management")
    print("-" * 50)
    
    while True:
        try:
            query = input("\nEnter your query: ").strip()
            
            if not query:
                print("Please enter a query or type '/help'.")
                continue

            if dispatch_command(query):
                continue

            # Process regular queries through the intelligent agent
            print(f"Processing: {query}")
            result = await run_intelligent_agent(query)
            if result:
                markdown = Markdown(result)
                console.print(markdown)
            else:
                print("No response from agent.")
                
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            return
        except EOFError:
            print("\nGoodbye!")
            return
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Type '/bye' to exit or continue with another query.")

def main() -> None:
    """Main CLI entry point."""
    args = parse_arguments()
    
    if args.memory:
        handle_command("memory", [args.memory])
        return
    if args.model:
        handle_command("model", [args.model])
        return
    
    # Determine the query to use
    query: str = args.query or args.query_arg
    
    if args.interactive:
        # Run in interactive mode
        try:
            asyncio.run(interactive_mode())
        except KeyboardInterrupt:
            return
    elif query:
        # Run single query
        print(f"Processing: {query}")
        result = asyncio.run(run_intelligent_agent(query))
        if result:
            markdown = Markdown(result)
            console.print(markdown)
        else:
            print("No response from agent.")

    else:
        # No query provided, show help
        print("No query provided. Use -h for help or -i for interactive mode.")
        print("\nQuick start:")
        print('  python testing.py "Your query here"')
        print('  python testing.py -i  # Interactive mode')
        print('  python testing.py --memory view  # View memory')
        sys.exit(1)

if __name__ == "__main__":
    main()