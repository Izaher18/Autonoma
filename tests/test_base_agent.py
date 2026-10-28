"""Tests for base agent functionality."""

import asyncio

import pytest
from core.base_agent import BaseAgent, AgentConfig
from core.tool_registry import tool


class DummyAgent(BaseAgent):
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
    agent = DummyAgent(name="MyAgent")
    assert agent.config.name == "MyAgent"
    assert isinstance(agent.config, AgentConfig)
    assert len(agent.conversation_history) == 0


def test_add_message():
    """Test adding messages to conversation history."""
    agent = DummyAgent()
    agent.add_message("user", "Hello")

    assert len(agent.conversation_history) == 1
    assert agent.conversation_history[0].role == "user"
    assert agent.conversation_history[0].content == "Hello"


def test_tool_registration():
    """Test that tools are automatically registered."""
    agent = DummyAgent()
    assert "test_tool" in agent.tools
    assert callable(agent.tools["test_tool"])


def test_call_tool():
    """Test calling a tool."""
    agent = DummyAgent()
    result = agent.call_tool("test_tool", {"input": "test"})
    assert result == "Processed: test"


def test_call_nonexistent_tool():
    """Test calling a non-existent tool raises error."""
    agent = DummyAgent()
    with pytest.raises(ValueError):
        agent.call_tool("nonexistent_tool", {})


def test_get_system_prompt():
    """Test getting system prompt."""
    agent = DummyAgent()
    prompt = agent.get_system_prompt()
    assert "TestAgent" in prompt
    assert "test_tool" in prompt


def test_reset():
    """Test resetting agent state."""
    agent = DummyAgent()
    agent.add_message("user", "Hello")
    agent.state["key"] = "value"

    agent.reset()

    assert len(agent.conversation_history) == 0
    assert len(agent.state) == 0


def test_execute():
    """Test synchronous execute method."""
    agent = DummyAgent()
    result = agent.execute("test task")
    assert "Received: test task" in result


def test_execute_inside_running_event_loop():
    """execute() must work when called from async code."""

    async def run():
        return DummyAgent().execute("from async")

    assert asyncio.run(run()) == "Received: from async"


def test_save_and_load_state(tmp_path):
    """State round-trips through a JSON file."""
    agent = DummyAgent(name="Saver")
    agent.add_message("user", "Hello")
    agent.state["key"] = "value"
    path = tmp_path / "state.json"
    agent.save_state(str(path))

    restored = DummyAgent()
    restored.load_state(str(path))
    assert restored.config.name == "Saver"
    assert restored.conversation_history[0].content == "Hello"
    assert restored.state == {"key": "value"}
