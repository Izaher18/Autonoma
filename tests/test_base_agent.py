"""Tests for base agent functionality."""

import pytest
from core.base_agent import BaseAgent, Message, AgentConfig
from core.tool_registry import tool


class TestAgent(BaseAgent):
    """Test agent implementation."""
    
    def __init__(self, name="TestAgent"):
        super().__init__(name=name)
    
    @tool(description="Test tool")
    def test_tool(self, input: str) -> str:
        """Test tool that returns the input."""
        return f"Processed: {input}"
    
    async def process(self, user_input: str) -> str:
        """Process test input."""
        return f"Received: {user_input}"


def test_agent_initialization():
    """Test agent initialization."""
    agent = TestAgent(name="MyAgent")
    assert agent.config.name == "MyAgent"
    assert isinstance(agent.config, AgentConfig)
    assert len(agent.conversation_history) == 0


def test_add_message():
    """Test adding messages to conversation history."""
    agent = TestAgent()
    agent.add_message("user", "Hello")
    
    assert len(agent.conversation_history) == 1
    assert agent.conversation_history[0].role == "user"
    assert agent.conversation_history[0].content == "Hello"


def test_tool_registration():
    """Test that tools are automatically registered."""
    agent = TestAgent()
    assert "test_tool" in agent.tools
    assert callable(agent.tools["test_tool"])


def test_call_tool():
    """Test calling a tool."""
    agent = TestAgent()
    result = agent.call_tool("test_tool", {"input": "test"})
    assert result == "Processed: test"


def test_call_nonexistent_tool():
    """Test calling a non-existent tool raises error."""
    agent = TestAgent()
    with pytest.raises(ValueError):
        agent.call_tool("nonexistent_tool", {})


def test_get_system_prompt():
    """Test getting system prompt."""
    agent = TestAgent()
    prompt = agent.get_system_prompt()
    assert "TestAgent" in prompt
    assert "test_tool" in prompt


def test_reset():
    """Test resetting agent state."""
    agent = TestAgent()
    agent.add_message("user", "Hello")
    agent.state["key"] = "value"
    
    agent.reset()
    
    assert len(agent.conversation_history) == 0
    assert len(agent.state) == 0


def test_execute():
    """Test synchronous execute method."""
    agent = TestAgent()
    result = agent.execute("test task")
    assert "Received: test task" in result
