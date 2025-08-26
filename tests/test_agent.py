"""
Test suite for the IntelligentAgent class
"""
import pytest
from unittest.mock import Mock, AsyncMock
from ollama_agent.core.agent import IntelligentAgent

class TestIntelligentAgent:
    """Test cases for IntelligentAgent"""
    
    def setup_method(self) -> None:
        """Set up test fixtures"""
        self.mock_tools = "test_tool: Test tool for unit tests"
        self.mock_functions = [{
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "Test tool for unit tests",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Test query"}
                    },
                    "required": ["query"]
                }
            }
        }]
        
        self.agent = IntelligentAgent(
            list_of_tools=self.mock_tools,
            avaliable_functions=self.mock_functions
        )
    
    def test_agent_initialization(self) -> None:
        """Test that agent initializes correctly"""
        assert self.agent.list_of_tools == self.mock_tools
        assert self.agent.avaliable_functions == self.mock_functions
    
    @pytest.mark.asyncio
    async def test_handle_user_query_simple(self) -> None:
        """Test handling a simple user query"""
        # Mock the MCP session
        mock_session = AsyncMock()
        
        # This would need more mocking in a real test
        # For now, just test that the method exists and accepts parameters
        query = "Test query"
        
        # Note: This test would need more setup to actually run
        # It's a template for future test development
        assert hasattr(self.agent, 'handle_user_query')
    
    def test_agent_has_required_attributes(self) -> None:
        """Test that agent has all required attributes"""
        required_attrs = ['list_of_tools', 'avaliable_functions']
        for attr in required_attrs:
            assert hasattr(self.agent, attr)