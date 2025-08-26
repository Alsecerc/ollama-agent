# Ollama Agent CLI

⚠️ **Project Status: Active Development** ⚠️
This project is currently under active development. While functional, some features may be incomplete or subject to change. Contributions and feedback are welcome!

A sophisticated AI agent system that leverages the Model Context Protocol (MCP) and Ollama to provide intelligent responses and tool execution capabilities through a global command-line interface.

## 🚀 Features

- **Global CLI Access**: Use `agent` command from anywhere on your system
- **Intelligent Tool Selection**: AI automatically decides when to use tools vs. direct responses  
- **Multi-Tool Integration**: Google search, CLI command execution, file system operations
- **Interactive & Single-Query Modes**: Flexible usage patterns for different needs
- **Memory Management**: Persistent conversation history with configurable limits
- **Model Configuration**: Support for multiple AI models (tiny, small, big) with auto-selection
- **Real-time Updates**: No reinstallation needed for code changes during development
- **Context-Aware Responses**: Maintains conversation context in interactive mode
- **One-Click Startup**: Automated system initialization and health checks

## 🏗️ Architecture

The system consists of several key components working together:

```
User Command → Global CLI → MCP Server → AI Agent → Ollama Models → Response
                ↓              ↓           ↓
            agent_cli.py → server.py → agent.py → Tool Execution
            testing.py (dev)
```

### Core Components

- **`agent_cli.py`**: Global CLI entry point with argument parsing and interactive mode
- **`testing.py`**: Development CLI with enhanced debugging and testing features
- **`agent/agent.py`**: Main intelligent agent with decision-making logic
- **`server/server.py`**: MCP server providing tools (search, CLI, file operations)
- **`agent/ai_model_lib.py`**: Ollama integration and model management
- **`model_loader.py`**: Configuration loader for AI model settings
- **`memory_manager.py`**: Persistent memory management with configurable limits
- **`startup.bat`**: Automated system initialization and health checks

## 📦 Quick Start

### Option 1: One-Click Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd ollamaAgent

# Run the automated startup script
startup.bat
```

The startup script will automatically:
- Check Python installation
- Start Ollama service if needed
- Download required AI models (gemma3:12b, gemma3:1b, gemma3:270m)
- Install Python dependencies
- Create .env template if missing
- Install global agent command
- Offer to start interactive mode

### Option 2: Manual Setup

1. **Clone and Navigate**
```bash
git clone <repository-url>
cd ollamaAgent
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure Environment**
Create a `.env` file with your API keys:
```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id
```

4. **Install Global CLI**
```bash
install_global_simple.bat
```

### Prerequisites
- Python 3.13+
- Ollama (will be started automatically by startup.bat)
- Git (for cloning)

## 🎯 Usage

### Single Query Mode
```bash
agent "List files in current directory"
agent "Search for recent AI news"
agent "Check Python version"
agent "What's trending in AI today?"
```

### Interactive Mode
```bash
agent -i
# or for development with enhanced debugging
python testing.py -i
```
In interactive mode, you can:
- Have ongoing conversations with context retention
- Use `/help` for assistance
- Use `/memory view`, `/memory clear` for memory management
- Use `/model summary` to view AI model configuration
- Type `/quit`, `/exit`, or `/bye` to exit gracefully
- Press Ctrl+C to force exit

### Memory Management Commands
```bash
# View current memory
python testing.py --memory view

# Clear memory (keep system prompt)
python testing.py --memory clear

# Clear all memory
python testing.py --memory clear-all

# Show memory statistics
python testing.py --memory stats
```

### Model Management Commands
```bash
# Show model configuration summary
python testing.py --model summary

# List available models
python testing.py --model models

# Show default models
python testing.py --model defaults

# Show full configuration
python testing.py --model config
```

### Available Commands
```bash
agent --help          # Show help and examples
agent --version       # Show version information
agent -q "query"      # Alternative query syntax
python testing.py -i  # Development mode with enhanced features
```

## 🛠️ Available Tools

The agent intelligently selects from these tools when needed:

1. **Google Search** (`google_search`)
   - Web search for current information, news, trends
   - Example: "What's the latest news in AI?"

2. **CLI Command Execution** (`execute_cli_command`)
   - Run system commands safely with security checks
   - Example: "Check Python version", "List running processes"

3. **Directory Listing** (`list_directory`)
   - Browse file systems and directory contents
   - Example: "List files in current directory", "What's in the data folder?"

## 🧠 How It Works

### Intelligent Decision Making
The agent uses a sophisticated three-model approach:
- **Tiny Model (gemma3:270m)**: Ultra-light for simple tasks
- **Small Model (gemma3:1b)**: Lightweight for quick responses and tool processing
- **Big Model (gemma3:12b)**: Full-featured for complex reasoning

### Tool Selection Logic
The AI automatically determines when to:
- Answer directly from its knowledge base
- Search the web for current/recent information
- Execute system commands for technical queries
- List directory contents for file operations
- Combine multiple tools for complex tasks

### Example Workflow
```
User: "What Python version am I running and what's the latest Python release?"
↓
Agent analyzes → Decides to use CLI tool + Google search
↓ 
Executes: python --version + searches "latest Python release"
↓
Processes both outputs → Returns comprehensive formatted response
```

## 📁 Project Structure

```
ollamaAgent/
├── install_global_simple.bat      # Global installation script
├── memory_manager.py              # Legacy memory management (root level)
├── model_loader.py                # Legacy model configuration loader (root level)
├── model.json                     # AI model configurations
├── pyproject.toml                 # Project metadata and build configuration
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies
├── startup.bat                    # One-click system initialization
├── testing.py                     # Development CLI with enhanced features
├── uv.lock                        # UV package manager lock file
├── __pycache__/                   # Python bytecode cache
├── data/
│   └── memory.json               # Persistent conversation memory
├── docs/
│   └── api.md                    # API documentation
├── examples/
│   └── basic_usage.py            # Usage examples and demos
├── scripts/
│   ├── install_global.bat        # Alternative installation script
│   └── startup.bat               # Alternative startup script
├── src/
│   ├── data/                     # Source data directory
│   └── ollama_agent/             # Main package directory
│       ├── __init__.py
│       ├── __pycache__/          # Package bytecode cache
│       ├── cli/                  # Command-line interface modules
│       │   ├── __init__.py
│       │   ├── dev.py            # Development CLI utilities
│       │   ├── main.py           # Main CLI entry point
│       │   └── __pycache__/
│       ├── config/               # Configuration management
│       │   ├── __init__.py
│       │   └── models.json       # Model configuration templates
│       ├── core/                 # Core functionality
│       │   ├── __init__.py
│       │   ├── agent.py          # Main intelligent agent logic
│       │   ├── ai_model_lib.py   # Ollama integration and model management
│       │   ├── memory_manager.py # Memory management system
│       │   ├── model_loader.py   # Model configuration loader
│       │   └── __pycache__/
│       └── server/               # MCP server implementation
│           ├── __init__.py
│           └── mcp_server.py     # MCP server with tool implementations
├── tasks/                        # Task definitions and workflows
└── tests/                        # Test suite
    ├── __init__.py
    └── test_agent.py             # Agent functionality tests
```

### Key Components

#### Root Level Files
- **`testing.py`**: Development CLI with enhanced debugging and testing features
- **`startup.bat`**: Automated system initialization and health checks
- **`install_global_simple.bat`**: Simple global CLI installation
- **`model.json`**: AI model configurations and parameters
- **`pyproject.toml`**: Modern Python project configuration
- **`requirements.txt`**: Python package dependencies
- **`uv.lock`**: UV package manager lock file for reproducible builds

#### Core Package (`src/ollama_agent/`)
- **`cli/main.py`**: Primary CLI entry point with argument parsing
- **`cli/dev.py`**: Development utilities and debugging tools
- **`core/agent.py`**: Main intelligent agent with decision-making logic
- **`core/ai_model_lib.py`**: Ollama integration and model management
- **`core/memory_manager.py`**: Persistent memory management system
- **`core/model_loader.py`**: Configuration loader for AI model settings
- **`server/mcp_server.py`**: MCP server providing tools (search, CLI, file operations)

#### Supporting Directories
- **`data/`**: Runtime data storage (memory, configurations)
- **`docs/`**: Project documentation and API references
- **`examples/`**: Usage examples and demonstration scripts
- **`scripts/`**: Installation and setup scripts
- **`tasks/`**: Task definitions and workflow configurations
- **`tests/`**: Test suite for functionality validation

#### Legacy Files (Root Level)
- **`memory_manager.py`**: Legacy memory management (kept for compatibility)
- **`model_loader.py`**: Legacy model loader (kept for compatibility)

### Architecture Overview
```
User Command → CLI (src/ollama_agent/cli/) → Core Agent (src/ollama_agent/core/) 
                ↓                              ↓
           MCP Server (src/ollama_agent/server/) → Ollama Models → Response
                ↓
        Tool Execution (search, CLI, file ops)
```

## ⚙️ Configuration

### Model Configuration (`model.json`)
Fine-tune AI model behavior, parameters, and selection rules:
- **tiny model**: Ultra-light (gemma3:270m) for simple tasks
- **small model**: Lightweight (gemma3:1b) for quick responses and tool processing  
- **big model**: Full-featured (gemma3:12b) for complex reasoning
- Temperature settings for creativity vs. precision
- Token limits for response length
- Timeout configurations for each model
- Model selection rules for different task types

### Memory Configuration
- Configurable memory limits (default: 15 messages)
- Automatic truncation when limits exceeded
- Persistent storage in `data/memory.json`
- System prompt preservation during memory clearing

### Environment Variables (`.env`)
```env
GOOGLE_API_KEY=your_google_api_key          # For web search functionality
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id  # Google Custom Search Engine ID
# Model names are now configured in model.json
```

## 🔄 Development

### Making Changes
✅ **No reinstallation needed!** The global CLI runs your code directly, so changes apply immediately.

### Development Mode
Use `python testing.py -i` for enhanced development features:
- Detailed debug output
- Memory management commands
- Model configuration inspection
- Error handling and troubleshooting

### Adding New Tools
1. Add tool functions to `server/server.py` with `@mcp.tool` decorators
2. Update tool descriptions and parameters
3. Test with `python testing.py -i` for immediate feedback

### Memory Management
- Memory automatically truncates when exceeding configured limits
- Use `/memory view` to inspect current conversation state
- Use `/memory clear` to reset while keeping system configuration
- Memory persists between sessions in `data/memory.json`

### Debugging
Enable detailed debug output in `agent.py`:
```python
printDebug = True  # Shows internal decision-making process
```

### System Health Check
Run `startup.bat` anytime to verify all components are working correctly.

## 🎓 Use Cases

### System Administration
```bash
agent "Show disk usage and memory stats"
agent "List running processes with high CPU usage"
agent "Check network connectivity to google.com"
agent "Find large files in the current directory"
```

### Development Tasks
```bash
agent "Find all Python files in this project"
agent "Run pytest and show results"
agent "Check git status and recent commits"
agent "Install numpy package via pip"
```

### Information Gathering
```bash
agent "Search for latest Python 3.14 features"
agent "What's trending in machine learning today?"
agent "Find documentation for FastAPI async functions"
agent "Compare performance of different sorting algorithms"
```

### Mixed Queries (Tool Combination)
```bash
agent "Check my Python version and find the latest Python release"
agent "List my project files and search for similar projects online"
agent "Show system specs and find compatible ML frameworks"
```

## 🚀 Daily Workflow

1. **Start your day**: Run `startup.bat` to ensure everything is ready
2. **Quick queries**: Use `agent "query"` for one-off questions
3. **Deep work**: Use `agent -i` for extended interactive sessions
4. **Development**: Make code changes - they apply immediately
5. **Troubleshooting**: Run `startup.bat` again if something breaks

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes (they apply immediately for testing)
4. Test thoroughly with `agent -i`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 🔧 Troubleshooting

### Quick Fixes
**Any issues?** → Run `startup.bat` first - it checks and fixes most problems automatically.

### Common Issues

| Issue | Solution |
|-------|----------|
| `agent` command not found | Run `install_global_simple.bat` |
| Import errors | Run `pip install -r requirements.txt` |
| Ollama connection failed | Run `startup.bat` to start Ollama service |
| API errors for Google search | Check your `.env` file has valid API keys |
| Models not found | Run `startup.bat` to download required models |
| Slow responses | Check if Ollama models are loaded (`ollama list`) |

### Advanced Troubleshooting
- **Debug mode**: Set `printDebug = True` in `agent/agent.py`
- **Check logs**: Look for error messages in the console output
- **Test components**: Run `python server/server.py` to test MCP server
- **Verify models**: Run `ollama list` to see available models

### Getting Help
- Run `agent --help` for usage information
- Use `agent -i` and type `help` for interactive assistance
- Check the debug output when `printDebug = True`
- Review the startup.bat output for system health status

---

**Happy AI-powered productivity!** 🤖✨