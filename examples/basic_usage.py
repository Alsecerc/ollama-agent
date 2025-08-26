# Basic Usage Example
"""
Simple examples of using the Ollama Agent CLI
"""

import asyncio
from ollama_agent.core.agent import IntelligentAgent
from ollama_agent.core.model_loader import ModelConfigLoader

async def basic_query_example() -> None:
    """Example of making a basic query to the agent"""
    
    # Load model configuration
    loader = ModelConfigLoader()
    
    # Create agent instance
    agent = IntelligentAgent(
        list_of_tools="Basic tools available",
        avaliable_functions=[]
    )
    
    # Example queries
    queries = [
        "What's the current date and time?",
        "List files in the current directory",
        "Search for recent AI news",
        "Check my Python version"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        print("🤖 Processing...")
        # Note: In real usage, you'd need to set up MCP session
        # This is just to show the interface
        print("✅ Response would appear here")

if __name__ == "__main__":
    asyncio.run(basic_query_example())