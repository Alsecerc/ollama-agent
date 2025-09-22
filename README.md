# Ollama Agent CLI

A local-first AI agent that runs on your machine using Ollama. Get intelligent responses and tool execution through a global command-line interface - no cloud dependencies.

## What It Does

- **Smart Tool Selection**: AI decides when to search web, run commands, or browse files
- **Global CLI Access**: Use `agent` command from anywhere
- **Local & Private**: All models run on your machine via Ollama
- **Interactive & Single-Query**: Flexible usage for different needs
- **Memory Persistence**: Maintains conversation context

## Quick Start

### One-Click Setup
```bash
git clone https://github.com/Alsecerc/ollamaAgent.git
cd ollamaAgent
startup.bat
```

The script automatically installs dependencies, downloads AI models, and sets up the global CLI.

### Manual Setup
```bash
git clone https://github.com/Alsecerc/ollamaAgent.git
cd ollamaAgent
pip install -e .
```

## Usage

### Single Commands
```bash
agent "List files in current directory"
agent "Search for latest AI news"
agent "Check Python version"
agent "What's trending in tech today?"
```

### Interactive Mode
```bash
agent -i
```

In interactive mode:
- Type questions naturally
- Use `/memory view`, `/memory clear` for memory management
- Type `/quit` to exit

## Available Tools

The AI automatically chooses from:

1. **Web Search** - Current information, news, trends
2. **CLI Commands** - System operations, development tasks
3. **File Operations** - Browse directories, list files

## Examples

```bash
# System tasks
agent "Show disk usage and running processes"
agent "Find Python files in this project"

# Information gathering
agent "Latest Python 3.14 features"
agent "Compare sorting algorithms"

# Mixed queries
agent "Check my Python version and find the latest release"
```

## Configuration

Create `.env` file for web search:
```env
GOOGLE_API_KEY=your_key
GOOGLE_SEARCH_ENGINE_ID=your_id
```

## Requirements

- Python 3.13+
- Ollama (auto-installed by startup.bat)

## Development

See [DEV_README.md](DEV_README.md) for development setup, architecture details, and contribution guidelines.

## License

MIT License - See [LICENSE](LICENSE) file.